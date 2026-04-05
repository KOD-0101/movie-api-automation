import streamlit as st


def poster_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"https://image.tmdb.org/t/p/w500{path}"


def initialize_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "selected_movie_id" not in st.session_state:
        st.session_state.selected_movie_id = None


def go_to_dashboard():
    st.session_state.page = "dashboard"
