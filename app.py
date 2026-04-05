import streamlit as st
from ui_helpers import initialize_session_state
from dashboard import render_home_page, render_dashboard_page

st.set_page_config(
    page_title="Movie Data Automation Project",
    layout="wide"
)

initialize_session_state()

if st.session_state.page == "home":
    render_home_page()
elif st.session_state.page == "dashboard":
    render_dashboard_page()
