import streamlit as st
import os
import re
from core import google_calendar as calendar
from core import gmail
from core.templates import MILESTONE_MAP, TEMPLATES, CC_LIST

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="TEXO Milestone Assistant", page_icon="📧", layout="wide")

# --- STYLE PREMIUM (Dark-Gold) ---
st.markdown("""
<style>
    /* --- TỐI ƯU HÓA CSS CHO CẢ 2 CHẾ ĐỘ --- */
    h1, h2, h3, h4, .main-header { color: #FFD700 !important; }
    
    .main-header { 
        font-weight: 800; 
        font-size: 32px; 
        text-align: center; 
        border-bottom: 2px solid #FFD700; 
        padding-bottom: 10px; 
        margin-bottom: 20px; 
    }
    
    .stButton>button { 
        background: linear-gradient(135deg, #152A4A 0%, #1e3a8a 100%) !important; 
        color: #FFD700 !important; 
        border: 1px solid #FFD700 !important; 
        border-radius: 12px; 
        font-weight: bold; 
        height: 3.5em; 
        width: 100%; 
    }
    .stButton>button:hover { 
        background: #FFD700 !important; 
        color: #0A1931 !important; 
        transform: scale(1.02); 
        transition: 0.2s; 
    }
    
    .preview-box { 
        background: var(--secondary-background-color); 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid rgba(255, 215, 0, 0.3); 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .sidebar-header { color: #FFD700 !important; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    
    /* Input field borders and background for visibility */
    .stTextInput div[data-baseweb="input"], .stTextArea div[data-baseweb="textarea"], .stSelectbox div[data-baseweb="select"] {
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
    }

    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; border-top: 1px solid rgba(255, 215, 0, 0.1); padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- XÁC THỰC ĐƠN GIẢN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #FFD700;'>🏦 TEXO MILESTONE</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Mật khẩu dự án:", type="password")
        if st.button("XÁC THỰC"):
            if pwd == "texo2026":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Truy cập không hợp lệ.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password(): st.stop()

# --- GIAO DIỆN CHÍNH ---
st.markdown("<div class='main-header'>📧 TEXO MILESTONE ASSISTANT</div>", unsafe_allow_html=True)

col_ctrl, col_main = st.columns([1, 2], gap="large")

with col_ctrl:
    st.markdown("<div class='sidebar-header'>📅 Điều khiển & Dữ liệu</div>", unsafe_allow_html=True)
    
    if st.button("🚀 QUÉT LỊCH DỰ ÁN HÔM NAY"):
        with st.spinner("Đang truy xuất Google Calendar..."):
            try:
                events = calendar.get_today_events()
                if not events:
                    st.warning("📅 Không tìm thấy sự kiện nào.")
                    st.session_state.events = []
                else:
                    st.session_state.events = events
                    st.success(f"✅ Đã tìm thấy {len(events)} sự kiện.")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
                st.info("💡 Lưu ý: Cần có file credentials.json hoặc cấu hình secrets để chạy online.")

    if "events" in st.session_state and st.session_state.events:
        summaries = [e.get('summary', 'Sự kiện không tên') for e in st.session_state.events]
        selected_event_summary = st.selectbox("Chọn sự kiện để xử lý:", summaries)
        
        # Phân tích sự kiện
        milestone_tag = next((tag for tag in MILESTONE_MAP if tag in selected_event_summary), None)
        
        if milestone_tag:
            template_idx = MILESTONE_MAP[milestone_tag]
            tpl = TEMPLATES[template_idx]
            
            # Bóc tách thông tin
            contract_match = re.search(r"\[(.+?)\]", selected_event_summary)
            contract_id = contract_match.group(1) if contract_match else "____"
            project_parts = selected_event_summary.split("-")
            project_name = project_parts[-1].strip() if len(project_parts) > 1 else selected_event_summary
            
            center_name = "Trung tâm quản lý"
            recipient = "tt@texo.com.vn"
            if "tt" in selected_event_summary.lower():
                 m = re.search(r"tt(\d+)", selected_event_summary.lower())
                 if m:
                     recipient = f"tt{m.group(1)}@texo.com.vn"
                     center_name = f"Trung tâm {m.group(1)}"
            
            # Điền dữ liệu vào template
            final_subject = tpl['subject'].replace("[Mã HĐ]", contract_id).replace("[Tên dự án]", project_name)
            final_body = tpl['body'].replace("[Tên dự án]", project_name).replace("[Mã HĐ]", contract_id).replace("[Tên Trung tâm]", center_name)
            
            st.session_state.current_draft = {"to": recipient, "subject": final_subject, "body": final_body}
            st.success(f"📍 Milestone detected: {milestone_tag}")
        else:
            st.warning("⏩ Sự kiện này không có mã Milestone hợp lệ.")
            st.session_state.current_draft = None
    else:
        st.info("Nhấn 'Quét lịch dự án' để bắt đầu.")

with col_main:
    st.markdown("<div class='sidebar-header'>📝 Nội dung Preview & Soạn thảo</div>", unsafe_allow_html=True)
    
    if "current_draft" in st.session_state and st.session_state.current_draft:
        draft = st.session_state.current_draft
        
        with st.container():
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            with c1: recipient_input = st.text_input("Người nhận (To):", value=draft['to'])
            with c2: st.text_input("CC:", value="P. Kỹ thuật & Lãnh đạo", disabled=True)
            
            subject_input = st.text_input("Tiêu đề (Subject):", value=draft['subject'])
            body_input = st.text_area("Nội dung Email (Markdown):", value=draft['body'], height=450)
            
            st.markdown("---")
            if st.button("📨 TẠO BẢN NHÁP TRÊN GMAIL MASTERS"):
                with st.spinner("Đang kết nối Gmail API..."):
                    try:
                        res = gmail.create_draft(recipient_input, subject_input, body_input, cc=CC_LIST)
                        st.success(f"🎉 Đã gửi bản nháp vào Hòm thư Nháp thành công!")
                        st.balloons()
                        st.code(f"Draft ID: {res['id']}", language="text")
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height: 400px; border: 2px dashed #333; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #666;'>Vui lòng chọn sự kiện có mã Milestone để bắt đầu soạn thảo</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>TEXO Engineering Department | Version 2.0 (Standalone) | Hoàng Đức Vũ</div>", unsafe_allow_html=True)
