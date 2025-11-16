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
