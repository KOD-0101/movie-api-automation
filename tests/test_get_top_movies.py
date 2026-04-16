import sqlite3
import pytest
from unittest.mock import patch, MagicMock


# Fake API response helpers

def make_movie(movie_id: int, title: str, rating: float = 7.5,
               votes: int = 1000, popularity: float = 20.0,
               release_date: str = "2022-01-01") -> dict:
    return {
        "id": movie_id,
        "title": title,
        "vote_average": rating,
        "vote_count": votes,
        "popularity": popularity,
        "release_date": release_date,
    }


def fake_response(movies: list) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"results": movies}
    return mock


def failed_response() -> MagicMock:
    mock = MagicMock()
    mock.status_code = 500
    return mock


# Tests

def test_main_inserts_valid_movies(tmp_path):
    """Valid movies from the API should be inserted into the database"""
    db_path = str(tmp_path / "movies.db")
    movies = [make_movie(1, "Inception"), make_movie(2, "The Dark Knight")]

    with patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
            patch("get_top_movies.requests.get", return_value=fake_response(movies)), \
            patch("get_top_movies.DB_PATH" if hasattr(__import__("get_top_movies"), "DB_PATH") else "builtins.open", db_path, create=True):

        import get_top_movies
        import importlib

        with patch.object(get_top_movies, "__file__", str(tmp_path / "get_top_movies.py")), \
                patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
                patch("get_top_movies.requests.get", return_value=fake_response(movies)):

            # Redirect DB to tmp_path by patching os.path.dirname
            with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)):
                get_top_movies.main()

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count > 0


def test_main_skips_invalid_movies(tmp_path):
    """Movies failing validation should not be inserted"""
    db_path = str(tmp_path / "movies.db")

    valid = make_movie(1, "Inception")
    invalid = {"id": None, "title": "", "vote_average": None,
               "vote_count": None, "popularity": None}

    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
            patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
            patch("get_top_movies.requests.get", return_value=fake_response([valid, invalid])):
        get_top_movies.main()

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT title FROM movies").fetchall()
    conn.close()

    titles = [r[0] for r in rows]
    assert "Inception" in titles
    assert "" not in titles


def test_main_exits_early_without_api_key(tmp_path, capsys):
    """main() should print an error and return if TMDB_API_KEY is missing"""
    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
            patch("get_top_movies.os.getenv", return_value=None):
        get_top_movies.main()

    captured = capsys.readouterr()
    assert "API key not found" in captured.out


def test_main_handles_failed_api_response(tmp_path):
    """A 500 response should be skipped without crashing"""
    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
            patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
            patch("get_top_movies.requests.get", return_value=failed_response()):
        get_top_movies.main()  # Should not raise

    conn = sqlite3.connect(db_path := str(tmp_path / "movies.db"))
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count == 0


def test_main_handles_empty_results(tmp_path):
    """An API response with no results should insert 0 rows"""
    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
            patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
            patch("get_top_movies.requests.get", return_value=fake_response([])):
        get_top_movies.main()

    conn = sqlite3.connect(str(tmp_path / "movies.db"))
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count == 0
