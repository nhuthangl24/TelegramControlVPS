# Telegram VPS Control Bot

Bot Telegram giúp điều khiển VPS từ xa thông qua giao diện Telegram. Hỗ trợ các tính năng như tạo phiên SSH, gửi lệnh, và quản lý phiên làm việc.

## Tính năng

- 🔐 **Phiên SSH tương tác**: Tạo các phiên làm việc SSH trực tiếp từ Telegram.
- 📡 **Truyền dữ liệu thời gian thực**: Hiển thị kết quả lệnh ngay trên Telegram.
- 🎛️ **Quản lý phiên làm việc**: Tạo, gửi lệnh, dừng và liệt kê các phiên SSH.
- 🔒 **Bảo mật**: Chỉ các tài khoản Telegram được ủy quyền mới có thể sử dụng bot.
- 📝 **Ghi log**: Lưu lại các hoạt động của bot vào file `telegram_remote_control.log`.

## Yêu cầu

- Python 3.7+
- Các thư viện Python:
  - `python-telegram-bot==20.6`
  - `paramiko`

## Cài đặt

1. Clone hoặc tải dự án này về máy.
2. Cài đặt các thư viện cần thiết:

```bash
pip install python-telegram-bot==20.6 paramiko
```

## Cấu hình

Chỉnh sửa các biến môi trường trong file `main.py`:

- `TG_TOKEN`: Token của bot Telegram.
- `AUTHORIZED_CHAT`: ID của tài khoản Telegram được phép sử dụng bot.
- `VPS_IP`: Địa chỉ IP của VPS.
- `VPS_USER`: Tên người dùng VPS.
- `VPS_PASS`: Mật khẩu VPS (khuyến nghị sử dụng SSH key thay vì mật khẩu).

## Sử dụng

1. Chạy bot:

```bash
python main.py
```

2. Các lệnh hỗ trợ:

- `/help`: Hiển thị danh sách các lệnh.
- `/session start <name> [command]`: Tạo phiên làm việc SSH mới.
- `/session send <name> <text>`: Gửi lệnh hoặc ký tự vào phiên làm việc.
- `/session stop <name>`: Dừng phiên làm việc.
- `/session list`: Liệt kê các phiên làm việc đang hoạt động.
- `/session tail <name> [lines]`: Xem log của phiên làm việc.
- `/run <command>`: Chạy một lệnh không tương tác.

## Cách sử dụng chi tiết

### 1. Khởi động bot

Chạy lệnh sau trong terminal để khởi động bot:

```bash
python main.py
```

Khi bot khởi động thành công, bạn sẽ thấy thông báo "Bot started" trong terminal.

### 2. Các lệnh hỗ trợ

#### Lệnh `/help`

Hiển thị danh sách các lệnh mà bot hỗ trợ:

```bash
/help
```

#### Lệnh `/session`

Quản lý các phiên làm việc SSH. Các tùy chọn:

- **Tạo phiên làm việc mới**:

  ```bash
  /session start <name> [command]
  ```

  - `<name>`: Tên của phiên làm việc.
  - `[command]` (tùy chọn): Lệnh sẽ được chạy ngay khi phiên làm việc được tạo.

  Ví dụ:

  ```bash
  /session start my_session
  /session start my_session ls -la
  ```

- **Gửi lệnh vào phiên làm việc**:

  ```bash
  /session send <name> <text>
  ```

  - `<name>`: Tên của phiên làm việc.
  - `<text>`: Lệnh hoặc ký tự cần gửi.

  Ví dụ:

  ```bash
  /session send my_session echo Hello
  ```

- **Dừng phiên làm việc**:

  ```bash
  /session stop <name>
  ```

  - `<name>`: Tên của phiên làm việc cần dừng.

  Ví dụ:

  ```bash
  /session stop my_session
  ```

- **Liệt kê các phiên làm việc đang hoạt động**:

  ```bash
  /session list
  ```

- **Xem log của phiên làm việc**:

  ```bash
  /session tail <name> [lines]
  ```

  - `<name>`: Tên của phiên làm việc.
  - `[lines]` (tùy chọn): Số dòng log cần xem (mặc định là 200).

  Ví dụ:

  ```bash
  /session tail my_session 100
  ```

#### Lệnh `/run`

Chạy một lệnh không tương tác trên VPS:

```bash
/run <command>
```

- `<command>`: Lệnh cần chạy.

Ví dụ:

```bash
/run uptime
/run df -h
```

### 3. Ghi chú quan trọng

- **Bảo mật**: Đảm bảo rằng chỉ các tài khoản Telegram được ủy quyền mới có thể sử dụng bot.
- **SSH Key**: Khuyến nghị sử dụng SSH key thay vì mật khẩu để tăng cường bảo mật.
- **Log**: Kiểm tra file `telegram_remote_control.log` để xem lại các hoạt động của bot.

## Ghi chú

- Đảm bảo rằng bot chỉ được sử dụng bởi các tài khoản được ủy quyền để tránh rủi ro bảo mật.
- Khuyến nghị sử dụng SSH key thay vì mật khẩu để tăng cường bảo mật.

## Đóng góp

Nếu bạn muốn đóng góp cho dự án, hãy tạo pull request hoặc mở issue trên GitHub.

## Giấy phép

Dự án này được phát hành dưới giấy phép MIT.
