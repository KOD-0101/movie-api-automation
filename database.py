import os
import sqlite3
import pandas as pd
from logger_setup import get_logger

logger = get_logger("database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DB_PATH is defined at module level so it can be patched in tests
# without modifying the function signature
DB_PATH = os.path.join(BASE_DIR, "movies.db")


def get_local_data() -> pd.DataFrame:
    """
    Reads the entire movies table from the local SQLite database
    and returns it as a pandas DataFrame.
    Used by the dashboard to populate the analytics section.
    """
    logger.info("Loading local movie data from database")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    logger.info(f"Loaded {len(df)} rows from local database")
    return df
