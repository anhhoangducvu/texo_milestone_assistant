# Hướng dẫn cấu hình Streamlit Secrets (Triển khai Online)

Để ứng dụng **TEXO Milestone Assistant** có thể chạy trên GitHub/Streamlit Cloud mà không cần file vật lý, Anh Vũ cần thực hiện các bước sau để "nạp" quyền truy cập vào hệ thống.

### Bước 1: Lấy nội dung Token từ máy cá nhân
Trên máy tính của Anh, hãy tìm và mở 2 file sau bằng Notepad (hoặc bất kỳ trình soạn thảo văn bản nào):
1. `token_calendar.json`
2. `token_gmail.json`

**Copy toàn bộ nội dung** (đoạn mã JSON) của từng file để chuẩn bị cho bước sau.

---

### Bước 2: Cấu hình trên Streamlit Cloud
1. Truy cập vào Dashboard của Streamlit Cloud (nơi Anh vừa tạo App).
2. Nhấn vào nút **Settings** (biểu tượng bánh răng) của App đó.
3. Chọn mục **Secrets** ở cột bên trái.
4. Paste nội dung theo cấu trúc dưới đây vào ô văn bản:

```toml
# Cấu hình Token cho Google Calendar
calendar_token = '''
[Dán nội dung từ file token_calendar.json vào đây]
'''

# Cấu hình Token cho Gmail
gmail_token = '''
[Dán nội dung từ file token_gmail.json vào đây]
'''
```

*Lưu ý: Giữ nguyên dấu nháy đơn ba `'''` để bọc nội dung JSON.*

---

### Bước 3: Lưu và Khởi động lại
- Nhấn **Save**.
- Streamlit Cloud sẽ tự động nhận diện thay đổi và khởi động lại App. 
- Bây giờ ứng dụng sẽ có quyền truy cập Lịch và Gmail mà không báo lỗi "không thấy lịch" nữa.

---

### 🛡️ Tại sao cách này an toàn?
- File `token.json` chứa quyền truy cập cá nhân. Nếu Anh đẩy lên GitHub, ai cũng có thể đọc được.
- **Streamlit Secrets** là một "két sắt" mã hóa, chỉ có ứng dụng của Anh mới có quyền đọc, giúp bảo vệ dữ liệu tuyệt đối.

> [!TIP]
> **Mẹo:** Nếu sau này token hết hạn (hiếm khi xảy ra), Anh chỉ cần chạy app ở máy Local để Google cấp token mới, sau đó cập nhật lại vào mục Secrets này là xong.
