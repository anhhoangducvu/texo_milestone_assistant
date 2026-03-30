import os
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 1. Cấu hình Scopes và đường dẫn
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
CREDS_FILE = 'credentials.json'

# Các điểm đến cần được cấp chìa khóa
TARGET_DIRS = [
    '.', # Thư mục hiện tại (Milestone App)
    '../../.agent/skills/google-calendar-integrator',
    '../../.agent/skills/gmail-integrator'
]

# Để localhost chạy được http (fix lỗi insecure_transport)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def authenticate(scopes, token_name):
    print(f"\n--- Đang xác thực {token_name.replace('token_', '').replace('.json', '')} ---")
    creds = None
    
    # Thử lấy từ file credentials.json chuẩn
    if not os.path.exists(CREDS_FILE):
        print(f"❌ Lỗi: Không tìm thấy file {CREDS_FILE} tại thư mục này!")
        return None
    
    try:
        # Khởi tạo quy trình xác thực (Dùng run_local_server cho ổn định nhất)
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, scopes)
        creds = flow.run_local_server(port=0, 
                                      authorization_prompt_message="Đăng nhập Google xong đừng tắt màn hình nhé...",
                                      success_message="Xác thực thành công! Bạn có thể quay lại terminal.")
        
        # Lưu chìa khóa ra file và sao chép tới các thư mục đích
        for target in TARGET_DIRS:
            if not os.path.exists(target):
                # Thử tạo thư mục nếu chưa có
                try: os.makedirs(target)
                except: continue
            
            dest_path = os.path.join(target, token_name)
            with open(dest_path, 'w') as token:
                token.write(creds.to_json())
            print(f"✅ Đã lưu/cập nhật: {dest_path}")
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình xác thực: {e}")
        return None
        
    return creds

if __name__ == '__main__':
    print("🚀 BẮT ĐẦU CẤP QUYỀN TRUY CẬP GOOGLE CHO HỆ SINH THÁI TEXO")
    print("Vui lòng đảm bảo các App Streamlit đang được TẮT để tránh xung đột.")
    
    try:
        authenticate(CALENDAR_SCOPES, 'token_calendar.json')
        authenticate(GMAIL_SCOPES, 'token_gmail.json')
        print("\n🎉 CHÚC MỪNG ANH VŨ! Hệ thống đã được cấp 'bùa hộ mệnh' thành công.")
        print("Tất cả App Streamlit và Lệnh /daily-email-check đã sẵn sàng hoạt động.")
    except Exception as e:
        print(f"\n❌ Có lỗi hệ thống: {e}")
    
    input("\nNhấn Enter để kết thúc...")
