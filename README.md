### 4. Ví dụ sử dụng thực tế

#### Tạo phiên làm việc SSH và chạy lệnh

1. Gửi lệnh để tạo phiên làm việc mới:

```bash
/session start my_session
```

2. Gửi lệnh vào phiên làm việc vừa tạo:

```bash
/session send my_session ls -la
```

3. Xem log của phiên làm việc:

```bash
/session tail my_session 50
```

4. Dừng phiên làm việc khi không cần sử dụng:

```bash
/session stop my_session
```

#### Chạy lệnh không tương tác

1. Gửi lệnh để kiểm tra trạng thái hệ thống:

```bash
/run uptime
```

2. Kiểm tra dung lượng ổ đĩa:

```bash
/run df -h
```

3. Xem danh sách các tiến trình đang chạy:

```bash
/run ps aux
```

### 5. Xử lý sự cố

- **Bot không phản hồi**:

  - Kiểm tra xem bot đã được khởi động chưa.
  - Đảm bảo rằng token Telegram và ID tài khoản được cấu hình đúng.

- **Không kết nối được VPS**:

  - Kiểm tra địa chỉ IP, tên người dùng và mật khẩu VPS.
  - Đảm bảo rằng VPS cho phép kết nối SSH từ địa chỉ IP của bạn.

- **Lỗi khi gửi lệnh**:
  - Đảm bảo rằng phiên làm việc đã được tạo trước khi gửi lệnh.
  - Kiểm tra log trong file `telegram_remote_control.log` để biết thêm chi tiết.

### 6. Bảo trì và nâng cấp

- **Cập nhật thư viện**:

  - Đảm bảo rằng các thư viện Python được cập nhật:

  ```bash
  pip install --upgrade python-telegram-bot paramiko
  ```

- **Kiểm tra log**:

  - Thường xuyên kiểm tra file log để phát hiện các vấn đề tiềm ẩn.

- **Bảo mật**:
  - Sử dụng SSH key thay vì mật khẩu để tăng cường bảo mật.
  - Hạn chế quyền truy cập vào bot chỉ cho các tài khoản được ủy quyền.

### 7. Hướng dẫn triển khai trên VPS

#### Bước 1: Cài đặt Python và các thư viện cần thiết

1. Đảm bảo rằng VPS của bạn đã cài đặt Python 3.7+.
2. Cài đặt các thư viện cần thiết:

```bash
pip install python-telegram-bot==20.6 paramiko
```

#### Bước 2: Cấu hình biến môi trường

1. Mở file `main.py` và chỉnh sửa các biến sau:

   - `TG_TOKEN`: Token của bot Telegram.
   - `AUTHORIZED_CHAT`: ID của tài khoản Telegram được phép sử dụng bot.
   - `VPS_IP`: Địa chỉ IP của VPS.
   - `VPS_USER`: Tên người dùng VPS.
   - `VPS_PASS`: Mật khẩu VPS (khuyến nghị sử dụng SSH key thay vì mật khẩu).

2. Hoặc thiết lập các biến môi trường trực tiếp trên VPS:

```bash
export TG_TOKEN="<token của bạn>"
export AUTHORIZED_CHAT_ID="<ID tài khoản Telegram>"
export VPS_IP="<IP VPS>"
export VPS_USER="<Tên người dùng VPS>"
export VPS_PASS="<Mật khẩu VPS>"
```

#### Bước 3: Chạy bot

1. Chạy lệnh sau để khởi động bot:

```bash
python main.py
```

2. Kiểm tra log trong file `telegram_remote_control.log` để đảm bảo bot hoạt động đúng.

#### Bước 4: Triển khai bot dưới dạng dịch vụ (tùy chọn)

1. Tạo file dịch vụ systemd:

```bash
sudo nano /etc/systemd/system/telegram_bot.service
```

2. Thêm nội dung sau:

```ini
[Unit]
Description=Telegram VPS Control Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/TelegramControlVPS
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Kích hoạt và khởi động dịch vụ:

```bash
sudo systemctl enable telegram_bot.service
sudo systemctl start telegram_bot.service
```

4. Kiểm tra trạng thái dịch vụ:

```bash
sudo systemctl status telegram_bot.service
```
