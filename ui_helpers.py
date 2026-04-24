import streamlit as st
from logger_setup import get_logger

logger = get_logger("ui_helpers")


def poster_url(path: str | None) -> str | None:
    """
    Builds a full TMDB poster image URL from the relative path
    returned by the API (e.g. "/abc123.jpg").
    Returns None if the path is empty or missing, the caller
    should check for None before rendering an image.
    """
    if not path:
        return None
    return f"https://image.tmdb.org/t/p/w500{path}"


def initialize_session_state():
    """
    Sets up the default session state values on first load.
    The 'in' check prevents overwriting values that are already
    set, important because Streamlit reruns the script on every
    interaction, so this function gets called repeatedly.
    """
    if "page" not in st.session_state:
        st.session_state.page = "home"
        logger.info("Initialized session state: page=home")

    if "selected_movie_id" not in st.session_state:
        st.session_state.selected_movie_id = None
        logger.info("Initialized session state: selected_movie_id=None")


def go_to_dashboard():
    """
    Navigation callback for the Get Started button on the home page.
    Changing st.session_state.page causes Streamlit to rerun the
    script, which picks up the new value and renders the dashboard.
    """
    st.session_state.page = "dashboard"
    logger.info("Navigated to dashboard page")
