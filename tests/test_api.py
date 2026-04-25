import pytest
from unittest.mock import patch, MagicMock

# Helpers


def mock_streamlit():
    """
    Builds a minimal Streamlit mock for tests that import api.py.
    api.py imports streamlit at the top level and uses st.cache_data
    as a decorator, both of those happen at import time, so Streamlit
    needs to be mocked before the module is imported or reloaded.
    cache_data is set to a passthrough so the decorated functions
    still run normally during tests.
    """
    st = MagicMock()
    st.secrets = {}
    st.cache_data = lambda **kwargs: (lambda f: f)
    return st


def fake_requests_response(data: dict, status_code: int = 200) -> MagicMock:
    """Mimics a requests.Response object with a given JSON body."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


# tmdb_get


def test_tmdb_get_returns_json(monkeypatch):
    # A successful API call should return the parsed JSON body
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    with patch(
        "api.requests.get", return_value=fake_requests_response({"results": [1, 2, 3]})
    ):
        result = api.tmdb_get("movie/popular")

    assert result == {"results": [1, 2, 3]}


def test_tmdb_get_raises_without_api_key(monkeypatch):
    # If TMDB_API_KEY is None, the function should raise ValueError
    # before even attempting a network request
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = None

    with pytest.raises(ValueError, match="TMDB_API_KEY not found"):
        api.tmdb_get("movie/popular")


def test_tmdb_get_calls_correct_url(monkeypatch):
    # The full TMDB base URL should be in the request — confirms the
    # endpoint is being appended to the right base
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    with patch("api.requests.get", return_value=fake_requests_response({})) as mock_get:
        api.tmdb_get("genre/movie/list")

    called_url = mock_get.call_args[0][0]
    assert "https://api.themoviedb.org/3/genre/movie/list" in called_url


# get_genres


def test_get_genres_returns_list(monkeypatch):
    # Should return the genres array from the API response
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    fake_genres = [{"id": 28, "name": "Action"}, {"id": 27, "name": "Horror"}]

    with patch(
        "api.requests.get", return_value=fake_requests_response({"genres": fake_genres})
    ):
        result = api.get_genres()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Action"


def test_get_genres_returns_empty_list_on_missing_key(monkeypatch):
    # If the API response doesn't include a 'genres' key,
    # the function should return an empty list rather than raise
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    with patch("api.requests.get", return_value=fake_requests_response({})):
        result = api.get_genres()

    assert result == []


# get_movies_by_genre


def test_get_movies_by_genre_returns_movies(monkeypatch):
    # Results from multiple pages should be combined into one list
    # 2 pages × 1 result each = 2 total
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    page_results = {"results": [{"id": 1, "title": "A Horror Movie"}]}

    with patch("api.requests.get", return_value=fake_requests_response(page_results)):
        result = api.get_movies_by_genre(27, pages=2)

    assert len(result) == 2
    assert result[0]["title"] == "A Horror Movie"


def test_get_movies_by_genre_empty_results(monkeypatch):
    # An empty results array from the API should return an empty list
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    with patch(
        "api.requests.get", return_value=fake_requests_response({"results": []})
    ):
        result = api.get_movies_by_genre(27, pages=1)

    assert result == []


# get_movie_details


def test_get_movie_details_returns_dict(monkeypatch):
    # Should return the full detail dict for the given movie ID
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    fake_detail = {"id": 550, "title": "Fight Club", "vote_average": 8.8}

    with patch("api.requests.get", return_value=fake_requests_response(fake_detail)):
        result = api.get_movie_details(550)

    assert result["title"] == "Fight Club"
    assert result["vote_average"] == 8.8
