import os
import base64
from email.message import EmailMessage
from email.policy import default
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

import streamlit as st
import json

def get_credentials():
    """Lấy thông tin xác thực từ tệp local hoặc Streamlit secrets một cách thông minh."""
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
    token_path = 'token_gmail.json'
    creds_path = 'credentials.json'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 🏟️ BƯỚC 1: Thử lấy từ Streamlit Secrets (Ưu tiên nhất cho cả Local & Online)
    try:
        if "gmail_token" in st.secrets:
            token_data = json.loads(st.secrets["gmail_token"])
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
            
            st.markdown(f"### 🔑 Cần xác thực Gmail")
            st.info("💡 Chìa khóa Secrets không khớp hoặc hết hạn. Anh Vũ hãy làm lại:")
            st.markdown(f"1. [👉 CLICK VÀO ĐÂY ĐỂ ĐĂNG NHẬP GMAIL]({auth_url})")
            st.markdown("2. Đăng nhập xong, Copy **URL** dán vào ô dưới:")
            
            auth_response = st.text_input("Dán URL tại đây (Gmail):", key=f"auth_resp_{flow_key}")
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
                    st.success("✅ Gmail đã sẵn sàng!")
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

def create_draft(to, subject, body_md, cc=""):
    """Tạo bản nháp Gmail từ Markdown."""
    creds = get_credentials()
    if not creds:
        raise Exception("Chưa cấu hình xác thực Gmail.")
    
    service = build('gmail', 'v1', credentials=creds)

    # Chuyển đổi MD sang HTML cơ bản
    html_body = body_md.replace("**", "<b>").replace("**", "</b>") # Rất thô sơ, nên dùng re hoặc library
    import re
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', body_md)
    html_body = html_body.replace('\n', '<br>')
    html_body = f"<div style='font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;'>{html_body}</div>"

    message = EmailMessage(policy=default.clone(max_line_length=0))
    message['To'] = to
    message['From'] = "me"
    if cc:
        message['Cc'] = cc
    message['Subject'] = subject

    message.set_content(body_md) # Fallback
    message.add_alternative(html_body, subtype='html')

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'message': {'raw': encoded_message}}

    draft = service.users().drafts().create(userId="me", body=create_message).execute()
    return draft
