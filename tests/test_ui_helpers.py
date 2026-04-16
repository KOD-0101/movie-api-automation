from unittest.mock import MagicMock
import importlib

# Helper


class FakeSessionState:
    """
    Mimics Streamlit session_state which supports both:
      st.session_state["key"]  and  st.session_state.key
    """

    def __init__(self, initial=None):
        self._data = initial or {}

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(key)
        return self._data.get(key)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self._data[key] = value


# poster_url


def test_poster_url_with_valid_path():
    from ui_helpers import poster_url

    assert poster_url("/abc123.jpg") == "https://image.tmdb.org/t/p/w500/abc123.jpg"


def test_poster_url_with_none():
    from ui_helpers import poster_url

    assert poster_url(None) is None


def test_poster_url_with_empty_string():
    from ui_helpers import poster_url

    assert poster_url("") is None


def test_poster_url_path_without_leading_slash():
    from ui_helpers import poster_url

    result = poster_url("abc123.jpg")
    assert result == "https://image.tmdb.org/t/p/w500abc123.jpg"


# initialize_session_state


def test_initialize_session_state_sets_page(monkeypatch):
    """Should set page='home' if not already in session state"""
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers

    importlib.reload(ui_helpers)
    ui_helpers.initialize_session_state()

    assert st_mock.session_state["page"] == "home"


def test_initialize_session_state_sets_selected_movie_id(monkeypatch):
    """Should set selected_movie_id=None if not already set"""
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers

    importlib.reload(ui_helpers)
    ui_helpers.initialize_session_state()

    assert st_mock.session_state["selected_movie_id"] is None


def test_initialize_session_state_does_not_overwrite(monkeypatch):
    """Should not overwrite existing session state values"""
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState(
        {"page": "dashboard", "selected_movie_id": 42}
    )
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers

    importlib.reload(ui_helpers)
    ui_helpers.initialize_session_state()

    assert st_mock.session_state["page"] == "dashboard"
    assert st_mock.session_state["selected_movie_id"] == 42


# go_to_dashboard


def test_go_to_dashboard_sets_page(monkeypatch):
    """go_to_dashboard should set session_state.page to 'dashboard'"""
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState(
        {"page": "home", "selected_movie_id": None}
    )
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers

    importlib.reload(ui_helpers)
    ui_helpers.go_to_dashboard()

    assert st_mock.session_state["page"] == "dashboard"
