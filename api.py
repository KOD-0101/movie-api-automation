import sqlite3
import os
from logger_setup import get_logger

logger = get_logger("analyze_movies")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movies.db")

logger.info("Analysis started")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\nTop 10 Highest Rated Movies:\n")
    logger.info("Running top rated movie query")

    cursor.execute("""
    SELECT title, rating
    FROM movies
    ORDER BY rating DESC
    LIMIT 10
    """)

    for row in cursor.fetchall():
        print(row)

    print("\nMost Popular Movies:\n")
    logger.info("Running most popular movie query")

    cursor.execute("""
    SELECT title, popularity
    FROM movies
    ORDER BY popularity DESC
    LIMIT 10
    """)

    for row in cursor.fetchall():
        print(row)

    print("\nAverage Movie Rating:\n")
    logger.info("Calculating average movie rating")

    cursor.execute("""
    SELECT AVG(rating)
    FROM movies
    """)

    print(cursor.fetchone()[0])

    conn.close()
    logger.info("Analysis completed successfully")

except Exception:
    logger.exception("Analysis failed")
    raise
