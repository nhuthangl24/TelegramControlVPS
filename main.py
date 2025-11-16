#!/usr/bin/env python3
# control_bot_stream.py
# Telegram <-> SSH interactive streaming (paramiko + python-telegram-bot)
# pip install python-telegram-bot==20.6 paramiko

import os, asyncio, shlex, paramiko, time
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------- CONFIG ----------
TG_TOKEN = os.environ.get("TG_TOKEN", "DAN TOKEN O DAY")
AUTHORIZED_CHAT = int(os.environ.get("AUTHORIZED_CHAT_ID", "ID O DAY"))
VPS_IP = os.environ.get("VPS_IP", "IP VPS")
VPS_USER = os.environ.get("VPS_USER", "root")
VPS_PASS = os.environ.get("VPS_PASS", "PASS VPS")   # strongly: use SSH key instead
# log file for bot actions
LOGFILE = Path("telegram_remote_control.log")
# ---------- END CONFIG ----------

SESSIONS = {}  # name -> { ssh_client, channel, task, chat_id, last_send_ts, buffer }

# utils
def log(txt):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        LOGFILE.write_text(LOGFILE.read_text() + f"[{ts}] {txt}\n")
    except Exception:
        try:
            with open(LOGFILE, "a") as f:
                f.write(f"[{ts}] {txt}\n")
        except Exception:
            pass

def ssh_connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # prefer key auth; this uses password - replace with key if possible
    c.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=10)
    return c

async def run_ssh_async(cmd, timeout=60):
    def _run():
        try:
            client = ssh_connect()
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
            out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
            client.close()
            return out
        except Exception as e:
            return f"[SSH ERROR] {e}"
    return await asyncio.to_thread(_run)

# streaming coroutine: reads from paramiko channel and sends to chat
async def session_reader(name):
    info = SESSIONS.get(name)
    if not info:
        return
    chan = info["channel"]
    chat_id = info["chat_id"]
    bot = info["bot"]
    buffer = ""
    last_sent = 0.0
    send_interval = 0.6   # seconds: group output and send every N secs to reduce messages
    max_chunk = 3500
    try:
        while True:
            await asyncio.sleep(0.2)
            if chan.recv_ready():
                data = chan.recv(4096).decode(errors="ignore")
                if not data:
                    continue
                buffer += data
                # if buffer contains newline or enough characters or enough time passed -> send
            if buffer and (time.time() - last_sent >= send_interval):
                # split into chunks by size, prefer sending complete lines
                # trim leading/trailing control sequences for readability
                text = buffer
                buffer = ""
                # Ctrl characters cleanup (keep basic)
                text = text.replace('\r\n', '\n')
                # send in chunks
                for chunk in [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]:
                    try:
                        await bot.send_message(chat_id=chat_id, text=f"```\n{chunk}\n```", parse_mode="Markdown")
                    except Exception as e:
                        # if sending fails, write to log and continue
                        log(f"send fail {name}: {e}")
                last_sent = time.time()
            # if channel closed, break
            if chan.exit_status_ready():
                # capture remaining output
                if chan.recv_ready():
                    data = chan.recv(4096).decode(errors="ignore")
                    if data:
                        try:
                            await bot.send_message(chat_id=chat_id, text=f"```\n{data}\n```", parse_mode="Markdown")
                        except:
                            pass
                await bot.send_message(chat_id=chat_id, text=f"⚠️ Session `{name}` ended (exit).")
                break
    except Exception as e:
        log(f"reader exception for {name}: {e}")
        try:
            await info["bot"].send_message(chat_id=info["chat_id"], text=f"❌ Reader error for {name}: {e}")
        except:
            pass
    finally:
        # cleanup
        try:
            chan.close()
        except: pass
        try:
            info["ssh"].close()
        except: pass
        SESSIONS.pop(name, None)
        log(f"session {name} closed")

# ---------- Bot handlers ----------
def is_auth(update: Update):
    return (update.effective_chat and update.effective_chat.id == AUTHORIZED_CHAT)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    text = (
        "/session start <name> [command]  — tạo session (persistent) và run optional command\n"
        "/session send <name> <text>     — gửi text/keystrokes vào session\n"
        "/session stop <name>            — dừng session\n"
        "/session list                   — liệt kê các session đang mở\n"
        "/session tail <name> [lines]    — capture pane (snapshot) của session\n"
        "/run <command>                  — chạy 1 command non-interactive\n"
    )
    await update.message.reply_text(text)

async def session_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not context.args:
        await update.message.reply_text("Usage: /session start <name> [command]")
        return
    name = context.args[0]
    cmd = " ".join(context.args[1:]) if len(context.args) > 1 else None
    if name in SESSIONS:
        await update.message.reply_text(f"Session `{name}` already exists.")
        return
    # create ssh and pty channel
    try:
        client = ssh_connect()
        transport = client.get_transport()
        chan = transport.open_session()
        chan.get_pty(term='xterm', width=200, height=50)
        chan.invoke_shell()
        # optional: run initial command
        if cmd:
            chan.send(cmd + "\n")
        # register session
        bot = context.bot
        SESSIONS[name] = {"ssh": client, "channel": chan, "chat_id": update.effective_chat.id, "bot": bot, "created": time.time()}
        # start reader task
        task = asyncio.create_task(session_reader(name))
        SESSIONS[name]["task"] = task
        await update.message.reply_text(f"✅ Created session `{name}`. Streaming output here.")
        log(f"SESSION_START {name} cmd={cmd}")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not create session: {e}")
        log(f"SESSION_START_FAIL {name} {e}")

async def session_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /session send <name> <text>")
        return
    name = context.args[0]
    text = " ".join(context.args[1:])
    info = SESSIONS.get(name)
    if not info:
        await update.message.reply_text("Session not found.")
        return
    try:
        info["channel"].send(text + "\n")
        await update.message.reply_text(f"Sent to `{name}`: `{text}`")
        log(f"SESSION_SEND {name} -> {text}")
    except Exception as e:
        await update.message.reply_text(f"Send failed: {e}")
        log(f"SESSION_SEND_FAIL {name} {e}")

async def session_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not context.args:
        await update.message.reply_text("Usage: /session stop <name>")
        return
    name = context.args[0]
    info = SESSIONS.get(name)
    if not info:
        await update.message.reply_text("Session not found.")
        return
    try:
        try:
            info["channel"].close()
        except: pass
        try:
            info["ssh"].close()
        except: pass
        # cancel task if running
        try:
            t = info.get("task")
            if t:
                t.cancel()
        except:
            pass
        SESSIONS.pop(name, None)
        await update.message.reply_text(f"Stopped session `{name}`.")
        log(f"SESSION_STOP {name}")
    except Exception as e:
        await update.message.reply_text(f"Error stopping session: {e}")
        log(f"SESSION_STOP_FAIL {name} {e}")

async def session_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not SESSIONS:
        await update.message.reply_text("(no sessions)")
        return
    lines = []
    for k,v in SESSIONS.items():
        created = datetime.fromtimestamp(v.get("created",0)).isoformat(timespec='seconds')
        lines.append(f"{k} (created {created})")
    await update.message.reply_text("\n".join(lines))

async def session_tail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not context.args:
        await update.message.reply_text("Usage: /session tail <name> [lines]")
        return
    name = context.args[0]
    lines = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 200
    tmux_has_session = False
    if not tmux_has_session :
        # We didn't implement tmux capture here; fallback: use `ps` to check and run `tmux capture-pane` via SSH
        try:
            out = await run_ssh_async(f"tmux capture-pane -pt {shlex.quote(name)} -S -{lines} && tmux show-buffer && tmux delete-buffer", timeout=15)
            if not out.strip():
                out = "(no output or tmux session not present)"
            for chunk in [out[i:i+3500] for i in range(0, len(out), 3500)]:
                await update.message.reply_text(f"```\n{chunk}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Tail error: {e}")

async def run_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return
    cmd = " ".join(context.args)
    await update.message.reply_text(f"Running: `{cmd}`", parse_mode="Markdown")
    out = await run_ssh_async(cmd, timeout=300)
    for chunk in [out[i:i+3500] for i in range(0, len(out), 3500)]:
        await update.message.reply_text(f"```\n{chunk}\n```", parse_mode="Markdown")

# fallback: treat plain messages as run only if they start with '!'
async def fallback_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    text = (update.message.text or "").strip()
    if not text:
        return
    # optional: treat messages starting with '!' as run command
    if text.startswith(""):
        cmd = text[:]
        out = await run_ssh_async(cmd, timeout=120)
        await update.message.reply_text(f"```\n{out}\n```", parse_mode="Markdown")

# ---------- main ----------
def main():
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("session", lambda u,c: asyncio.create_task(session_dispatch(u,c))))
    # simpler: explicit mappings
    app.add_handler(CommandHandler("run", run_command_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_msg))
    print("Bot started")
    app.run_polling()

# helper to dispatch "session" subcommands: /session start name ...
async def session_dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update): return
    if not context.args:
        await update.message.reply_text("Usage: /session <start|send|stop|list|tail> ...")
        return
    action = context.args[0].lower()
    # shift args for subhandler
    context.args = context.args[1:]
    if action == "start":
        await session_start(update, context)
    elif action == "send":
        await session_send(update, context)
    elif action == "stop":
        await session_stop(update, context)
    elif action == "list":
        await session_list(update, context)
    elif action == "tail":
        await session_tail(update, context)
    else:
        await update.message.reply_text("Unknown session action. Use start/send/stop/list/tail")

if __name__ == "__main__":
    main()