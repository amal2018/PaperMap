import streamlit as st

st.set_page_config(page_title="Welcome", page_icon="assets/br_logo.png", layout="wide")

# --- Align Help Expander to Top Right ---
col1, col2 = st.columns([7, 3])
with col2:
    with st.expander("❓ Help", expanded=False):
        st.markdown("""
        **Contact:**  
        📧 [amalrenv@gmail.com](https://mail.google.com/mail/?view=cm&to=amalrenv@gmail.com
)  
        
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

**Get started by clicking below!**
""")

# --- Navigation Button ---
if st.button("Start Mapping ➡️"):
    st.switch_page("pages/01_🟢_Data_Upload_and_Study_Area_Map.py")
