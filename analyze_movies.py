import sqlite3
import os
from logger_setup import get_logger

logger = get_logger("analyze_movies")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DB_PATH at module level so it can be patched during testing
DB_PATH = os.path.join(BASE_DIR, "movies.db")


def main():
    """
    Runs three SQL queries against the local movies database and
    prints the results to the terminal. Useful for quick inspection
    of the data without opening the full Streamlit dashboard.
    """
    logger.info("Analysis started")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query 1 — top 10 by rating, highest first
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

        # Query 2 — top 10 by TMDB popularity score, highest first
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

        # Query 3 — average rating across all records in the table
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
        # Log the full traceback and re-raise so the caller knows it failed
        logger.exception("Analysis failed")
        raise


if __name__ == "__main__":
    main()
