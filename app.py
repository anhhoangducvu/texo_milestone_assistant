# -*- coding: utf-8 -*-
"""TEXO – Soạn email nhắc việc dự án theo lịch Google (Milestone Assistant).
Đọc sự kiện hôm nay trên lịch TEXO → nhận diện mốc [M-W01]…[M-6M] → điền mẫu email → tạo bản nháp Gmail.
Phòng Kỹ thuật – Công ty CP TEXO Tư vấn và Đầu tư.

Chạy:  streamlit run app.py
"""
import re

import streamlit as st

from core import gmail, ui
from core import google_calendar as calendar
from core.templates import CC_LIST, MILESTONE_MAP, TEMPLATES

APP_VERSION = "2.1"
TITLE = "Soạn email nhắc việc theo lịch dự án"
ui.setup("TEXO · " + TITLE, "📧")
ui.gate("Soạn email nhắc việc dự án")


def find_tag(summary):
    return next((tag for tag in MILESTONE_MAP if tag in (summary or "")), None)


def build_draft(event, tag):
    """Điền mẫu email theo mốc – ưu tiên thông tin trong ghi chú sự kiện, sau đó đến tiêu đề."""
    summary = event.get("summary", "")
    desc = event.get("description", "")
    tpl = TEMPLATES[MILESTONE_MAP[tag]]
    contract_id = project_name = None
    if desc:
        m = re.search(r"Mã HĐ:\s*([^\n\r]+)", desc, re.IGNORECASE)
        if m:
            contract_id = m.group(1).strip()
        short = re.search(r"Tên viết ngắn:\s*([^\n\r]+)", desc, re.IGNORECASE)
        proj = re.search(r"Dự án:\s*([^\n\r]+)", desc, re.IGNORECASE)
        if short and short.group(1).strip():
            project_name = short.group(1).strip()
        elif proj:
            project_name = proj.group(1).strip()
    if not contract_id:
        parts = [p.strip() for p in summary.split("-")]
        if parts and parts[0] != tag:
            contract_id = parts[0]
        else:
            for m in re.findall(r"\[(.+?)\]", summary):
                if f"[{m}]" != tag:
                    contract_id = m
                    break
            contract_id = contract_id or "____"
    if not project_name:
        parts = summary.split("-")
        project_name = parts[-1].strip() if len(parts) > 1 else summary

    center_name, recipient = "Trung tâm quản lý", "tt@texo.com.vn"
    m = re.search(r"tt(\d+)", summary.lower())
    if m:
        recipient = f"tt{m.group(1)}@texo.com.vn"
        center_name = f"Trung tâm {m.group(1)}"
    subject = tpl["subject"].replace("[Mã HĐ]", contract_id).replace("[Tên dự án]", project_name)
    body = (tpl["body"].replace("[Tên dự án]", project_name).replace("[Mã HĐ]", contract_id)
            .replace("[Tên Trung tâm]", center_name))
    return {"to": recipient, "subject": subject, "body": body, "tag": tag, "title": tpl.get("title", "")}


# --------------------------------------------------------------------------- thanh bên
with st.sidebar:
    st.markdown("### 🔗 Kết nối Google")
    try:
        creds_cal = calendar.get_credentials()
        if creds_cal:
            ui.badge("Google Calendar: đã kết nối", "green")
        creds_gmail = gmail.get_credentials()
        if creds_gmail:
            ui.badge("Gmail: đã kết nối", "green")
    except Exception as e:
        st.error(f"⚠️ Cần xác thực: {e}")
        st.stop()
    st.caption("Đọc lịch tên **TEXO**; email chỉ tạo **bản nháp** trong Gmail, anh/chị tự xem lại rồi gửi.")
    st.divider()
    ui.logout_button()
    st.caption(f"Soạn email nhắc việc v{APP_VERSION} · Xây dựng: Hoàng Đức Vũ")

# --------------------------------------------------------------------------- trang chính
ui.header(TITLE, "Phòng Kỹ thuật · Quét mốc dự án hôm nay trên Google Calendar → soạn email theo mẫu TEXO → "
                 "tạo bản nháp Gmail")

with st.expander("📘 Hướng dẫn sử dụng"):
    st.markdown("""
1. Bấm **Quét lịch dự án hôm nay** – app đọc các sự kiện hôm nay trên lịch TEXO.
2. Chọn sự kiện. Sự kiện có mã mốc `[M-W01]`, `[M-W02]`, `[M-W04]`, `[M-W06]`, `[M-W08]`, `[M-W10]`, `[M-W12]`, `[M-6M]`
   (do app *Thiết lập lịch dự án* tạo) sẽ được điền sẵn mẫu email: Mã HĐ, tên dự án, Trung tâm.
3. Sửa người nhận, tiêu đề, nội dung nếu cần → bấm **Tạo bản nháp trên Gmail**.
4. Mở Gmail, xem lại bản nháp rồi gửi.
""")

events = st.session_state.get("events") or []
draft = st.session_state.get("current_draft")
kpi_box = st.container()

col_ctrl, col_main = st.columns([1, 2], gap="large")

with col_ctrl:
    st.markdown("##### 📅 Lịch dự án")
    if st.button("🔄 Quét lịch dự án hôm nay", type="primary", use_container_width=True):
        with st.spinner("Đang đọc Google Calendar…"):
            try:
                found = calendar.get_today_events() or []
                st.session_state.events = found
                st.session_state.current_draft = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
                st.caption("Cần có credentials.json (chạy ở máy) hoặc cấu hình Secrets (chạy online).")

    if events:
        selected = st.selectbox("Chọn sự kiện để soạn email", events,
                                format_func=lambda x: ("📌 " if find_tag(x.get("summary", "")) else "· ")
                                + x.get("summary", "Sự kiện không tên"))
        tag = find_tag(selected.get("summary", ""))
        if tag:
            st.session_state.current_draft = build_draft(selected, tag)
            ui.callout(f"🟢 Nhận diện mốc <b>{tag}</b> – {TEMPLATES[MILESTONE_MAP[tag]].get('title', '')}", "green")
        else:
            st.session_state.current_draft = None
            ui.callout("🟠 Sự kiện này không có mã mốc hợp lệ – không có mẫu email.", "orange")
        draft = st.session_state.current_draft
    elif "events" in st.session_state:
        st.info("📅 Hôm nay không có sự kiện nào trên lịch TEXO.")
    else:
        st.info("Bấm **Quét lịch dự án hôm nay** để bắt đầu.")

with col_main:
    st.markdown("##### 📝 Xem trước & soạn email")
    if draft:
        c1, c2 = st.columns([2, 1])
        recipient_input = c1.text_input("Người nhận (To)", value=draft["to"])
        c2.text_input("CC", value=f"Lãnh đạo & P.KT ({len(CC_LIST.split(','))} địa chỉ)", disabled=True,
                      help=CC_LIST)
        subject_input = st.text_input("Tiêu đề", value=draft["subject"])
        body_input = st.text_area("Nội dung email (Markdown)", value=draft["body"], height=450)
        if st.button("📨 Tạo bản nháp trên Gmail", type="primary", use_container_width=True):
            with st.spinner("Đang kết nối Gmail…"):
                try:
                    res = gmail.create_draft(recipient_input, subject_input, body_input, cc=CC_LIST)
                    ui.callout("🟢 Đã tạo bản nháp trong hộp thư Nháp của Gmail – mở Gmail xem lại rồi gửi.", "green")
                    st.caption(f"Mã bản nháp: {res['id']}")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
    else:
        st.markdown("<div style='text-align:center; color:#64748b; padding:110px 20px;'>Chưa có email để soạn.<br>"
                    "Quét lịch rồi chọn một sự kiện có mã mốc ở cột bên trái.</div>", unsafe_allow_html=True)

# Ô tổng hợp (vẽ sau cùng để phản ánh sự kiện vừa chọn, hiển thị ở đầu trang)
with kpi_box:
    n_tag = sum(1 for e in events if find_tag(e.get("summary", "")))
    scanned = "events" in st.session_state
    k = st.columns(3)
    ui.kpi(k[0], len(events) if scanned else "–", "Sự kiện hôm nay", "trên lịch TEXO")
    ui.kpi(k[1], n_tag if scanned else "–", "Có mã mốc", "soạn được email", "green" if n_tag else "blue")
    ui.kpi(k[2], draft["tag"] if draft else "–", "Mốc đang soạn",
           draft["title"] if draft else "chưa chọn sự kiện", "orange" if draft else "grey")
