import os
import base64
from email.message import EmailMessage
from email.policy import default
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

import streamlit as st
import json

def get_credentials():
    """Lấy thông tin xác thực từ tệp local hoặc Streamlit secrets."""
    creds = None
    token_path = 'token_gmail.json'
    creds_path = 'credentials.json'
    
    # 1. Thử lấy từ File Local
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        return creds

    # 2. Thử lấy từ Streamlit Secrets
    if "gmail_token" in st.secrets:
        token_data = json.loads(st.secrets["gmail_token"])
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        return creds
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                return None
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
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
