import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Page Settings ---
st.set_page_config(page_title="Feedback & Analytics", page_icon="assets/br_logo.png", layout="wide")

# --- Help Expander ---
col1, col2 = st.columns([7, 3])
with col2:
    with st.expander("❓ Help", expanded=False):
        st.markdown("📧 [amalrenv@gmail.com](mailto:amalrenv@gmail.com)")

# --- Logo & Title ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("assets/PaperMap_logo.png", width=180)

st.title("💬 Feedback & User Analytics")

# --- Google Sheets Setup ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

gc = gspread.authorize(credentials)
spreadsheet = gc.open("PaperMap-feedback")  # Make sure you create this sheet
worksheet = spreadsheet.sheet1

# --- Feedback Form ---
with st.form("feedback_form"):
    satisfaction = st.slider("How satisfied are you with PaperMap?", 1, 5, 3)
    feature_request = st.text_area("Any new features you'd like to see?")
    comments = st.text_area("Additional comments or suggestions?")
    submitted = st.form_submit_button("Submit Feedback")

    if submitted:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([timestamp, satisfaction, feature_request, comments])
        st.success("🎉 Thank you for your feedback!")

# --- Link Back ---
if st.button("⬅️ Back to Composite Layout"):
    st.switch_page("pages/03_🖼️_Composite_Layout_and_Download.py")
