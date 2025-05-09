import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from pytz import timezone

# --- Page Settings ---
st.set_page_config(page_title="Welcome", page_icon="assets/br_logo.png", layout="wide")

# --- Align Help Expander to Top Right ---
col1, col2 = st.columns([7, 3])
with col2:
    with st.expander("❓ Help", expanded=False):
        st.markdown("""
        **Contact:**  
        📧 [amalrenv@gmail.com](https://mail.google.com/mail/?view=cm&to=amalrenv@gmail.com)  
        """)

# --- Logo Centered at Top ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/PaperMap_logo.png", width=180)

# --- Title & Description ---
st.title("🏠 Welcome to PaperMap")
st.markdown("""
This app helps you generate **publication-quality study area maps** for your research papers:
1. **Data Upload & Study Area Map:** Upload your CSV, xls, or xlsx file and customize your main study area map.
2. **Overview Maps (limited to India):** Automatically generate India, State, and District overview maps.
3. **Composite Layout (limited to India):** Download a professional composite layout for your paper.

**Please fill a few quick details before you start!**
""")

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
spreadsheet = gc.open("PaperMap-users")
worksheet = spreadsheet.sheet1

# --- Session State to Track Form Submission ---
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# --- User Info Form ---
if not st.session_state.form_submitted:
    with st.form("user_info_form"):
        name = st.text_input("Name (optional)", max_chars=50)
        affiliation = st.selectbox("Affiliation", ["Select...", "Academic", "Industry", "Research Institute", "Government", "NGO", "Other"])
        organization = st.text_input("Organization/Institute Name", max_chars=100)
        email = st.text_input("Email (optional)", max_chars=100)
        purpose = st.text_area("Purpose of using PaperMap (optional)", height=100)

        submitted = st.form_submit_button("Submit")

        if submitted:
            if affiliation == "Select..." or not organization.strip():
                st.error("Please fill Affiliation and Organization to proceed.")
            else:
                ist = timezone('Asia/Kolkata')
                timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
                worksheet.append_row([timestamp, name, affiliation, organization, email, purpose])
                st.success("Thank you! You can now start mapping.")
                st.session_state.form_submitted = True

# --- Navigation Button After Form Submitted ---
if st.session_state.form_submitted:
    if st.button("Start Mapping ➡️"):
        st.switch_page("pages/01_🟢_Data_Upload_and_Study_Area_Map.py")

# --- Affiliation Chart (Bottom of Page) ---
st.markdown("---")
st.subheader("📊 Current User Stats")

# Fetch data from sheet and convert to DataFrame
records = worksheet.get_all_records()
df = pd.DataFrame(records)

if not df.empty and "Affiliation" in df.columns:
    affiliation_counts = df['Affiliation'].value_counts()
    affiliation_labels = affiliation_counts.index.tolist()
    affiliation_values = affiliation_counts.values.tolist()

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for i, (label, value) in enumerate(zip(affiliation_labels, affiliation_values)):
        fig.add_trace(go.Bar(
            y=["Users"],
            x=[value],
            name=f"{label} ({value})",
            orientation='h',
            marker=dict(color=colors[i % len(colors)]),
            hovertemplate=f'{label}: {value}<extra></extra>'
        ))

    fig.update_layout(
        barmode='stack',
        title_text=f"Total Users: {len(df)}",
        xaxis_title="Number of Users",
        yaxis=dict(showticklabels=False),
        height=200,
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor='center'),
        plot_bgcolor='#f0f0f5'
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No user data available yet to generate the chart.")



