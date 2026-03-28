import os
import datetime
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TEXO_CALENDAR_ID = 'c3b53b35d280ce52410261d8d1d443c95955183833c771e6fcabe31d236a026a@group.calendar.google.com'

import streamlit as st
import json

def get_credentials():
    """Lấy thông tin xác thực từ tệp local hoặc Streamlit secrets."""
    creds = None
    token_path = 'token_calendar.json'
    creds_path = 'credentials.json'
    
    # THẾ TRẬN 1: Thử lấy từ File Local (cho phát triển local)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        return creds

    # THẾ TRẬN 2: Thử lấy từ Streamlit Secrets (cho chạy Online/GitHub)
    # Cần cấu hình trong [secrets] với key "calendar_token"
    if "calendar_token" in st.secrets:
        token_data = json.loads(st.secrets["calendar_token"])
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        return creds

    # THẾ TRẬN 3: Nếu chưa có Token, yêu cầu xác thực mới (Local duy nhất)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                return None
        
        # Lưu lại token sau khi xác thực thành công (chỉ ở Local)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def get_today_events():
    """Truy xuất danh sách sự kiện hôm nay."""
    creds = get_credentials()
    if not creds:
        return []
    
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    
    events_result = service.events().list(
        calendarId=TEXO_CALENDAR_ID, 
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])
