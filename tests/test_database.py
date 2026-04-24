import sqlite3
import pandas as pd
from unittest.mock import patch


# Helpers


def create_temp_db(path: str):
    """
    Builds a small test database at the given path.
    Used in every test so each one starts with a clean, known state.
    pytest's tmp_path fixture handles cleanup after each test run.
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE movies (
            movie_id INTEGER,
            date TEXT,
            title TEXT,
            rating REAL,
            votes INTEGER,
            release_date TEXT,
            popularity REAL,
            category TEXT
        )
    """)
    cursor.executemany(
        "INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "2024-01-01", "Inception", 8.8, 25000, "2010-07-16", 55.3, "top_rated"),
            (
                2,
                "2024-01-01",
                "The Dark Knight",
                9.0,
                30000,
                "2008-07-18",
                80.1,
                "top_rated",
            ),
            (
                3,
                "2024-01-01",
                "Interstellar",
                8.6,
                20000,
                "2014-11-07",
                45.2,
                "popular",
            ),
        ],
    )
    conn.commit()
    conn.close()


# Tests


def test_get_local_data_returns_dataframe(tmp_path):
    # The function should return a DataFrame, not a list or dict
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    # Patch DB_PATH so the function reads from our temp DB, not movies.db
    with patch("database.DB_PATH", db_path):
        from database import get_local_data
        df = get_local_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


def test_get_local_data_has_expected_columns(tmp_path):
    # Check the key columns are all present in the returned DataFrame
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("database.DB_PATH", db_path):
        from database import get_local_data
        df = get_local_data()

    expected_columns = {"movie_id", "title", "rating", "popularity", "category"}
    assert expected_columns.issubset(set(df.columns))


def test_get_local_data_correct_values(tmp_path):
    # The data coming back should match what was inserted
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("database.DB_PATH", db_path):
        from database import get_local_data
        df = get_local_data()

    titles = set(df["title"].tolist())
    assert "Inception" in titles
    assert "The Dark Knight" in titles


def test_get_local_data_ratings_in_range(tmp_path):
    # All ratings should fall between 0 and 10 — catches schema issues
    db_path = str(tmp_path / "movies.db")
    create_temp_db(db_path)

    with patch("database.DB_PATH", db_path):
        from database import get_local_data
        df = get_local_data()

    assert df["rating"].between(0, 10).all()


def test_get_local_data_empty_table(tmp_path):
    # An empty table should return an empty DataFrame, not raise an error
    db_path = str(tmp_path / "movies.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE movies (
            movie_id INTEGER, date TEXT, title TEXT, rating REAL,
            votes INTEGER, release_date TEXT, popularity REAL, category TEXT
        )
    """)
    conn.commit()
    conn.close()

    with patch("database.DB_PATH", db_path):
        from database import get_local_data
        df = get_local_data()

    assert isinstance(df, pd.DataFrame)
    assert df.empty
