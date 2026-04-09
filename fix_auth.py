import os
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 1. Cấu hình Scopes và đường dẫn
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
# Tự động lấy thư mục hiện tại của script để tìm file credentials.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(BASE_DIR, 'credentials.json')

# Các điểm đến cần được cấp chìa khóa
TARGET_DIRS = [
    BASE_DIR, # Thư mục Milestone App
    os.path.abspath(os.path.join(BASE_DIR, '../../.agent/skills/google-calendar-integrator')),
    os.path.abspath(os.path.join(BASE_DIR, '../../.agent/skills/gmail-integrator'))
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
        token_json = creds.to_json()
        for target in TARGET_DIRS:
            if not os.path.exists(target):
                # Thử tạo thư mục nếu chưa có
                try: os.makedirs(target)
                except: continue
            
            dest_path = os.path.join(target, token_name)
            with open(dest_path, 'w') as token:
                token.write(token_json)
            print(f"✅ Đã lưu/cập nhật: {dest_path}")
        
        # --- KAIZEN: In ra chuỗi để dán vào Streamlit Secrets ---
        secret_key = token_name.replace('.json', '')
        print(f"\n🔑 CHÌA KHÓA CHO STREAMLIT SECRETS ({secret_key}):")
        print("-" * 50)
        # Ép chuỗi JSON về dạng một dòng để dễ copy
        import json
        clean_json = json.dumps(json.loads(token_json))
        print(f'{secret_key} = \'{clean_json}\'')
        print("-" * 50)
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình xác thực: {e}")
        return None
        
    return creds

if __name__ == '__main__':
    print("🚀 BẮT ĐẦU CẤP QUYỀN TRUY CẬP GOOGLE CHO HỆ SINH THÁI TEXO")
    print("Vui lòng đảm bảo các App Streamlit đang được TẮT để tránh xung đột.")
    
    try:
        # Xác thực từng cái và in ra secrets
        authenticate(CALENDAR_SCOPES, 'calendar_token.json') # Đổi tên cho đồng bộ với code logic
        authenticate(GMAIL_SCOPES, 'gmail_token.json')
        
        # --- KAIZEN: In thêm google_credentials ---
        import json
        with open(CREDS_FILE, 'r') as f:
            creds_data = json.load(f)
            creds_str = json.dumps(creds_data)
        
        print("\n" + "="*60)
        print("🎉 CHÚC MỪNG ANH VŨ! Hệ thống đã được cấp 'bùa hộ mệnh' thành công.")
        print("CÁC BƯỚC ĐỂ SIÊU BẢO MẬT & CHẠY ONLINE VĨNH VIỄN:")
        print("1. Vào Settings -> Secrets trên Streamlit Cloud.")
        print("2. Dán TOÀN BỘ các dòng dưới đây vào mục Secrets:")
        print("-" * 50)
        print(f"google_credentials = '{creds_str}'")
        # Chờ authenticate in calendar_token và gmail_token ở trên rồi
        print("-" * 50)
        print("3. QUAN TRỌNG: Anh hãy xóa các file .json trong folder trước khi up")
        print("   lên GitHub hoặc đảm bảo .gitignore đã chặn chúng để bảo mật nhé!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Có lỗi hệ thống: {e}")
    
    input("\nNhấn Enter để kết thúc...")
