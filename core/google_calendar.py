import os
import datetime
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# CHO PHÉP CHẠY HTTP Ở LOCAL (Fix lỗi insecure_transport)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_texo_calendar_id(service):
    """Tìm ID của lịch 'TEXO'. Nếu không thấy, trả về 'primary'."""
    try:
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list.get('items', []):
            if entry['summary'] == 'TEXO':
                return entry['id']
    except: pass
    return 'primary'

import streamlit as st
import json

def get_credentials():
    """Lấy thông tin xác thực từ tệp local hoặc Streamlit secrets một cách thông minh."""
    creds = None
    # Xác định đường dẫn tuyệt đối để tránh lỗi relative path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(base_dir, 'token_calendar.json')
    creds_path = os.path.join(base_dir, 'credentials.json')
    
    # 🏟️ BƯỚC 1: Thử lấy từ File Local
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            st.warning(f"⚠️ File token cũ bị hỏng, đang yêu cầu xác thực lại: {e}")
            os.remove(token_path)
            creds = None

    # 🏜️ BƯỚC 2: Thử lấy từ Streamlit Secrets (Chỉ khi chạy online)
    if not creds and os.environ.get("STREAMLIT_SHARING_AUTHOR"):
        try:
            if "calendar_token" in st.secrets:
                token_data = json.loads(st.secrets["calendar_token"])
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except:
            pass

    # 🛡️ BƯỚC 3: KIỂM TRA HIỆU LỰC & LÀM MỚI (REFRESH)
    if creds:
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                return creds
            except Exception as e:
                st.warning(f"🔄 Không thể làm mới chìa khóa cũ: {e}")
                creds = None

    # 🔑 BƯỚC 4: XÁC THỰC THỦ CÔNG (Nếu các bước trên thất bại)
    if not creds or not creds.valid:
        if os.path.exists(creds_path):
            # Dùng session_state để GIỮ FLOW (tránh mất state khi RERUN)
            flow_key = f"flow_{os.path.basename(token_path)}"
            if flow_key not in st.session_state:
                st.session_state[flow_key] = InstalledAppFlow.from_client_secrets_file(
                    creds_path, 
                    SCOPES, 
                    redirect_uri='http://localhost'
                )
            
            flow = st.session_state[flow_key]
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            
            st.markdown(f"### 🔑 Cần cấp quyền truy cập Google Calendar")
            st.info("⚠️ Chìa khóa cũ đã hết hạn hoặc chưa được cấp. Anh Vũ hãy làm theo các bước:")
            st.markdown(f"1. [👉 CLICK VÀO ĐÂY ĐỂ ĐĂNG NHẬP]({auth_url})")
            st.markdown("2. Đăng nhập xong, Copy **TOÀN BỘ địa chỉ (URL)** trên trình duyệt dán vào ô dưới:")
            
            auth_response = st.text_input(f"Dán URL kết quả tại đây:", key=f"auth_resp_{flow_key}")
            if auth_response:
                try:
                    # Chuẩn hóa link
                    if "http://" in auth_response and "localhost" not in auth_response:
                        auth_response = auth_response.replace("http://", "https://")
                    
                    flow.fetch_token(authorization_response=auth_response)
                    creds = flow.credentials
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                    
                    # Dọn dẹp session_state để không bị lặp
                    del st.session_state[flow_key]
                    
                    st.success("✅ Xác thực thành công! Anh hãy bấm Quét lịch dự án lần nữa nhé.")
                    st.balloons()
                    st.rerun() # Quan trọng: Rerun để load creds từ file vừa lưu
                except Exception as e:
                    st.error(f"❌ Lỗi xác thực: {str(e)}")
                    st.warning("⚠️ Có thể link này đã dùng rồi hoặc quá hạn. Hãy click lại link ở bước 1 để lấy link mới.")
                    del st.session_state[flow_key]
                    st.stop()
            else:
                st.stop()
        else:
            st.error(f"❌ Thiếu tệp cấu hình {creds_path}. Không thể cấp quyền.")
            return None
            
    return creds

def get_today_events():
    """Truy xuất danh sách sự kiện hôm nay."""
    creds = get_credentials()
    if not creds:
        return []
    
    service = build('calendar', 'v3', credentials=creds)
    
    # Sử dụng múi giờ Việt Nam (UTC+7) để đảm bảo đồng bộ khi chạy trên server (UTC)
    vn_tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(vn_tz)
    
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    
    calendar_id = get_texo_calendar_id(service)
    events_result = service.events().list(
        calendarId=calendar_id, 
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])
