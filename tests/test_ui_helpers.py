from unittest.mock import MagicMock
import importlib


# Helper: session_state mock


class FakeSessionState:
    """
    Streamlit's session_state supports both dict-style and attribute-style access:
      st.session_state["page"]  and  st.session_state.page
    A plain Python dict only supports the first style, which causes AttributeError
    when the real code uses the second. This class replicates both access patterns
    so the tests behave the same way the real Streamlit environment does.
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
        # Private attributes (like _data) go through normal attribute lookup
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
    # A path starting with / should be appended directly to the base URL
    from ui_helpers import poster_url
    assert poster_url("/abc123.jpg") == "https://image.tmdb.org/t/p/w500/abc123.jpg"


def test_poster_url_with_none():
    # None means TMDB didn't return a poster, should get None back
    from ui_helpers import poster_url
    assert poster_url(None) is None


def test_poster_url_with_empty_string():
    # Empty string is treated the same as None
    from ui_helpers import poster_url
    assert poster_url("") is None


def test_poster_url_path_without_leading_slash():
    # No slash means the URL won't have a separator, this is expected behaviour,
    # not a bug we're trying to prevent
    from ui_helpers import poster_url
    result = poster_url("abc123.jpg")
    assert result == "https://image.tmdb.org/t/p/w500abc123.jpg"


# initialize_session_state


def test_initialize_session_state_sets_page(monkeypatch):
    # First call with empty session state should set page to 'home'
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers
    importlib.reload(ui_helpers)
    ui_helpers.initialize_session_state()

    assert st_mock.session_state["page"] == "home"


def test_initialize_session_state_sets_selected_movie_id(monkeypatch):
    # selected_movie_id should default to None when not already set
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers
    importlib.reload(ui_helpers)
    ui_helpers.initialize_session_state()

    assert st_mock.session_state["selected_movie_id"] is None


def test_initialize_session_state_does_not_overwrite(monkeypatch):
    # If values are already set, the function should leave them alone,
    # Streamlit reruns the script on every interaction so this matters
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
    # Calling go_to_dashboard() should flip page from 'home' to 'dashboard'
    st_mock = MagicMock()
    st_mock.session_state = FakeSessionState(
        {"page": "home", "selected_movie_id": None}
    )
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import ui_helpers
    importlib.reload(ui_helpers)
    ui_helpers.go_to_dashboard()

    assert st_mock.session_state["page"] == "dashboard"
