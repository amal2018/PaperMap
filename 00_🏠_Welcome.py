import streamlit as st

st.set_page_config(page_title="Welcome", layout="wide")

# Center the logo at the top using columns
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("assets/PaperMap_logo.png", width=180)

st.title("🏠 Welcome to PaperMap")

st.markdown("""
This app helps you generate **publication-quality study area maps** for your research papers:
1. **Data Upload & Study Area Map:** Upload your CSV file and customize your main study area map.
2. **Overview Maps:** Automatically generate India, State, and District overview maps.
3. **Composite Layout:** Download a professional composite layout for your paper.

**Get started by clicking below!**
""")

if st.button("Start Mapping ➡️"):
    st.switch_page("pages/01_🟢_Data_Upload_and_Study_Area_Map.py")
