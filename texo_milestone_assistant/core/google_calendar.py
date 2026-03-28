import os
import datetime
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TEXO_CALENDAR_ID = 'c3b53b35d280ce52410261d8d1d443c95955183833c771e6fcabe31d236a026a@group.calendar.google.com'

def get_credentials():
    """Lấy thông tin xác thực từ tệp local hoặc Streamlit secrets."""
    creds = None
    # Thử lấy từ File Local (cho phát triển local)
    token_path = 'token_calendar.json'
    creds_path = 'credentials.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                # Nếu không có file, có thể user đang chạy trên Streamlit Cloud
                # Ở đây chúng ta sẽ báo lỗi để user cấu hình secrets sau
                return None
        
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
