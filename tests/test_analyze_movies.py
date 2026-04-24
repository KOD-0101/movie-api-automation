import sqlite3
import pytest
from unittest.mock import patch


# Helpers


def create_temp_db(path: str):
    """Spins up a small test database with known data for each test."""
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE movies (
            movie_id INTEGER, date TEXT, title TEXT, rating REAL,
            votes INTEGER, release_date TEXT, popularity REAL, category TEXT
        )
    """)
    cursor.executemany(
        "INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "2024-01-01", "Inception", 8.8, 25000, "2010-07-16", 55.3, "top_rated"),
            (2, "2024-01-01", "The Dark Knight", 9.0, 30000, "2008-07-18", 80.1, "top_rated"),
            (3, "2024-01-01", "Interstellar", 8.6, 20000, "2014-11-07", 45.2, "popular"),
            (4, "2024-01-01", "Parasite", 8.5, 18000, "2019-05-30", 30.0, "popular"),
            (5, "2024-01-01", "Everything Everywhere", 7.8, 15000, "2022-03-25", 20.5, "popular"),
        ],
    )
    conn.commit()
    conn.close()


# Tests


def test_main_runs_without_error(tmp_path, capsys):
    # Basic smoke test — make sure main() completes and prints all three sections
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("analyze_movies.DB_PATH", db_path):
        from analyze_movies import main
        main()

    captured = capsys.readouterr()
    assert "Top 10 Highest Rated Movies" in captured.out
    assert "Most Popular Movies" in captured.out
    assert "Average Movie Rating" in captured.out


def test_main_outputs_top_rated_correctly(tmp_path, capsys):
    # The Dark Knight has rating 9.0, Inception has 8.8
    # Dark Knight should appear first in the output
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("analyze_movies.DB_PATH", db_path):
        from analyze_movies import main
        main()

    captured = capsys.readouterr()
    dark_knight_pos = captured.out.find("The Dark Knight")
    inception_pos = captured.out.find("Inception")

    assert dark_knight_pos != -1
    assert inception_pos != -1
    assert dark_knight_pos < inception_pos


def test_main_outputs_average_rating(tmp_path, capsys):
    # The printed average should be a valid float between 0 and 10
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("analyze_movies.DB_PATH", db_path):
        from analyze_movies import main
        main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")

    # Average rating is the last line printed
    avg_line = lines[-1].strip()
    avg = float(avg_line)
    assert 0 <= avg <= 10


def test_main_outputs_most_popular(tmp_path, capsys):
    # The Dark Knight has popularity 80.1, highest in the test data
    # so it should appear first in the Most Popular section
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("analyze_movies.DB_PATH", db_path):
        from analyze_movies import main
        main()

    captured = capsys.readouterr()
    popular_section = captured.out.split("Most Popular Movies:")[1]
    assert "The Dark Knight" in popular_section.split("Average Movie Rating:")[0]


def test_main_raises_on_missing_db(tmp_path):
    # Pointing at a path that doesn't exist should raise an exception
    missing_path = str(tmp_path / "nonexistent.db")

    with patch("analyze_movies.DB_PATH", missing_path):
        from analyze_movies import main
        with pytest.raises(Exception):
            main()
