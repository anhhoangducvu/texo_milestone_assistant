# 📧 Soạn email nhắc việc theo lịch dự án – TEXO (Milestone Assistant) – v2.1

Ứng dụng Streamlit độc lập giúp tự động hóa việc soạn thảo Email nhắc việc dự án theo các mốc Milestone từ Google Calendar.

## ✨ Tính năng chính
- **Quét lịch dự án:** Tự động nhận diện 8 loại Milestone (`[M-W01]` đến `[M-6M]`).
- **Soạn thảo thông minh:** Tự động điền [Mã HĐ], [Tên Dự Án], [Tên Trung tâm] vào mẫu chuẩn TEXO.
- **Gmail Integration:** Tạo bản nháp trực tiếp vào Gmail cá nhân.
- **Giao diện v2.1:** đồng bộ bộ app Phòng Kỹ thuật – đăng nhập gọn có logo TEXO, đầu trang logo + tiêu đề, ô tổng hợp (sự kiện hôm nay, sự kiện có mã mốc, mốc đang soạn), nút Đăng xuất, giao diện sáng cố định. Giao diện dùng chung ở `core/ui.py`, logo ở `assets/logo_texo.png`.
- **Bảo mật GitHub:** `.gitignore` chặn `credentials.json`, `token*.json`, `secrets.toml`.

## 🚀 Hướng dấn cài đặt nhanh (Local)

1. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Cấu hình Google API:**
   - Đảm bảo có file `credentials.json` trong thư mục gốc.
   - Chạy ứng dụng lần đầu để kích hoạt xác thực và lưu `token.json`.

3. **Chạy ứng dụng:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Triển khai Online (Streamlit Cloud)

Khi đẩy lên GitHub và deploy lên Streamlit Cloud, hãy cấu hình các xác thực thông qua **Secrets** của Streamlit để đảm bảo an toàn.

---
_Người xây dựng: Hoàng Đức Vũ – Phòng Kỹ thuật._
