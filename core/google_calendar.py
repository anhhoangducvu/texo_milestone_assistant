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
    # Đường dẫn tệp
    token_path = 'token_calendar.json'
    creds_path = 'credentials.json'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 🏟️ BƯỚC 1: Thử lấy từ Streamlit Secrets (Ưu tiên nhất cho cả Local & Online)
    try:
        if "calendar_token" in st.secrets:
            token_data = json.loads(st.secrets["calendar_token"])
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    return creds
                except: pass
    except: pass

    # 🏟️ BƯỚC 2: Thử lấy từ File Local (Quét cả root và cha)
    paths_to_check = [token_path, os.path.join(base_dir, token_path)]
    for p in paths_to_check:
        if os.path.exists(p):
            try:
                creds = Credentials.from_authorized_user_file(p, SCOPES)
                if creds and creds.valid: return creds
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        with open(p, 'w') as f:
                            f.write(creds.to_json())
                        return creds
                    except: pass
            except: pass

    # 🔑 BƯỚC 3: XÁC THỰC THỦ CÔNG (Nếu các bước trên thất bại)
    if not creds or not creds.valid:
        # Tìm file credentials.json
        c_paths = [creds_path, os.path.join(base_dir, creds_path)]
        final_creds_path = next((cp for cp in c_paths if os.path.exists(cp)), None)
        
        if final_creds_path:
            flow_key = f"flow_{token_path}"
            if flow_key not in st.session_state:
                st.session_state[flow_key] = InstalledAppFlow.from_client_secrets_file(
                    final_creds_path, SCOPES, redirect_uri='http://localhost'
                )
            flow = st.session_state[flow_key]
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            
            st.markdown(f"### 🔑 Cần xác thực Google Calendar")
            st.info("💡 Chìa khóa Secrets không khớp hoặc hết hạn. Anh Vũ hãy làm lại:")
            st.markdown(f"1. [👉 CLICK VÀO ĐÂY ĐỂ ĐĂNG NHẬP]({auth_url})")
            st.markdown("2. Đăng nhập xong, Copy **URL** dán vào ô dưới:")
            
            auth_response = st.text_input("Dán URL tại đây:", key=f"auth_resp_{flow_key}")
            if auth_response:
                try:
                    if "http://" in auth_response and "localhost" not in auth_response:
                        auth_response = auth_response.replace("http://", "https://")
                    flow.fetch_token(authorization_response=auth_response)
                    creds = flow.credentials
                    # Lưu lại local để dùng lần sau
                    with open(os.path.join(base_dir, token_path), 'w') as f:
                        f.write(creds.to_json())
                    del st.session_state[flow_key]
                    st.success("✅ Xác thực thành công! Hệ thống đang tải lại...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
                    del st.session_state[flow_key]
                    st.stop()
            else:
                st.stop()
        else:
            st.error(f"❌ Không thấy file credentials.json")
            return None
    return creds
            
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
