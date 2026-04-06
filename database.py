import os
import sqlite3
import pandas as pd
from logger_setup import get_logger

logger = get_logger("database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movies.db")


def get_local_data() -> pd.DataFrame:
    logger.info("Loading local movie data from database")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    logger.info(f"Loaded {len(df)} rows from local database")
    return df
