import pytest
from unittest.mock import patch, MagicMock

# Helpers


def mock_streamlit():
    """Return a MagicMock that stands in for the streamlit module."""
    st = MagicMock()
    st.secrets = {}
    st.cache_data = lambda **kwargs: (lambda f: f)
    return st


def fake_requests_response(data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


# tmdb_get


def test_tmdb_get_returns_json(monkeypatch):
    """tmdb_get should return parsed JSON from a successful response"""
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
    """tmdb_get should raise ValueError if API key is None"""
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = None

    with pytest.raises(ValueError, match="TMDB_API_KEY not found"):
        api.tmdb_get("movie/popular")


def test_tmdb_get_calls_correct_url(monkeypatch):
    """tmdb_get should call the correct TMDB base URL"""
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
    """get_genres should return a list of genre dicts"""
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
    """get_genres should return [] if API response has no 'genres' key"""
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
    """get_movies_by_genre should return combined results across pages"""
    st_mock = mock_streamlit()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import api

    importlib.reload(api)

    api.TMDB_API_KEY = "fake_key"

    page_results = {"results": [{"id": 1, "title": "A Horror Movie"}]}

    with patch("api.requests.get", return_value=fake_requests_response(page_results)):
        result = api.get_movies_by_genre(27, pages=2)

    # 2 pages × 1 result each
    assert len(result) == 2
    assert result[0]["title"] == "A Horror Movie"


def test_get_movies_by_genre_empty_results(monkeypatch):
    """get_movies_by_genre should return [] if API returns no results"""
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
    """get_movie_details should return the full movie detail dict"""
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
