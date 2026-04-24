import streamlit as st
from logger_setup import get_logger
from ui_helpers import initialize_session_state
from dashboard import render_home_page, render_dashboard_page

logger = get_logger("app")

# Page config must be the first Streamlit call in the script
st.set_page_config(page_title="Movie Data Automation Project", layout="wide")

logger.info("App started")

# Set up session state defaults before anything tries to read them
initialize_session_state()

# Route to the correct page based on session state
# Streamlit reruns this entire script on every user interaction,
# so the routing logic runs on every rerun
if st.session_state.page == "home":
    render_home_page()
elif st.session_state.page == "dashboard":
    render_dashboard_page()
