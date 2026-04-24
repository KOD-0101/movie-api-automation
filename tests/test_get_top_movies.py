import sqlite3
from unittest.mock import patch, MagicMock


# Fake API response helpers


def make_movie(
    movie_id: int,
    title: str,
    rating: float = 7.5,
    votes: int = 1000,
    popularity: float = 20.0,
    release_date: str = "2022-01-01",
) -> dict:
    """Builds a minimal movie dict in the shape TMDB returns."""
    return {
        "id": movie_id,
        "title": title,
        "vote_average": rating,
        "vote_count": votes,
        "popularity": popularity,
        "release_date": release_date,
    }


def fake_response(movies: list) -> MagicMock:
    """Mimics a successful 200 response from the TMDB API."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"results": movies}
    return mock


def failed_response() -> MagicMock:
    """Mimics a 500 error response from the TMDB API."""
    mock = MagicMock()
    mock.status_code = 500
    return mock


# Tests 


def test_main_inserts_valid_movies(tmp_path):
    # Valid records should end up in the database after main() runs
    db_path = str(tmp_path / "movies.db")
    movies = [make_movie(1, "Inception"), make_movie(2, "The Dark Knight")]

    import get_top_movies

    # Patch dirname so the DB is created in the temp directory,
    # patch getenv so no real API key is needed,
    # patch requests.get so no real HTTP call is made
    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
         patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
         patch("get_top_movies.requests.get", return_value=fake_response(movies)):
        get_top_movies.main()

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count > 0


def test_main_skips_invalid_movies(tmp_path):
    # Records that fail validation should not appear in the database
    db_path = str(tmp_path / "movies.db")

    valid = make_movie(1, "Inception")
    invalid = {
        "id": None,
        "title": "",
        "vote_average": None,
        "vote_count": None,
        "popularity": None,
    }

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
    # If TMDB_API_KEY isn't set, main() should print an error and return
    # without trying to connect to the API or the database
    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
         patch("get_top_movies.os.getenv", return_value=None):
        get_top_movies.main()

    captured = capsys.readouterr()
    assert "API key not found" in captured.out


def test_main_handles_failed_api_response(tmp_path):
    # A 500 error from the API should be logged and skipped,
    # not crash the script, the database should end up empty
    db_path = str(tmp_path / "movies.db")

    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
         patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
         patch("get_top_movies.requests.get", return_value=failed_response()):
        get_top_movies.main()

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count == 0


def test_main_handles_empty_results(tmp_path):
    # An API response that returns no movies should result in 0 rows,
    # not an error
    db_path = str(tmp_path / "movies.db")

    import get_top_movies

    with patch("get_top_movies.os.path.dirname", return_value=str(tmp_path)), \
         patch("get_top_movies.os.getenv", return_value="fake_api_key"), \
         patch("get_top_movies.requests.get", return_value=fake_response([])):
        get_top_movies.main()

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    assert count == 0
