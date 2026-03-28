# 📧 TEXO Milestone Assistant (Standalone)

Ứng dụng Streamlit độc lập giúp tự động hóa việc soạn thảo Email nhắc việc dự án theo các mốc Milestone từ Google Calendar.

## ✨ Tính năng chính
- **Quét lịch dự án:** Tự động nhận diện 8 loại Milestone (`[M-W01]` đến `[M-6M]`).
- **Soạn thảo thông minh:** Tự động điền [Mã HĐ], [Tên Dự Án], [Tên Trung tâm] vào mẫu chuẩn TEXO.
- **Gmail Integration:** Tạo bản nháp trực tiếp vào Gmail cá nhân.
- **Premium Interface:** Giao diện Dark-Gold sang trọng, tối ưu cho Anh Vũ (TEXO).

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
**Phát triển bởi:** Hoàng Đức Vũ - Phòng Kỹ thuật TEXO.
