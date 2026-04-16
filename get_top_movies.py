import requests
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from logger_setup import get_logger
from validation import is_valid_movie

load_dotenv()
logger = get_logger("get_top_movies")


def main():
    API_KEY = os.getenv("TMDB_API_KEY")

    if not API_KEY:
        logger.error("API key not found")
        print("Error: API key not found.")
        return

    today = datetime.today().strftime("%Y-%m-%d")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "movies.db")

    logger.info("Movie ingestion started")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS movies")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
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

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_movies_unique
    ON movies (movie_id, date, category)
    """)

    logger.info("Database connection established and table checked")

    endpoints = {
        "top_rated": "movie/top_rated",
        "popular": "movie/popular",
        "now_playing": "movie/now_playing",
        "upcoming": "movie/upcoming",
    }

    pages_to_fetch = 5

    total_inserted = 0
    total_skipped = 0

    for category, endpoint in endpoints.items():
        for page in range(1, pages_to_fetch + 1):
            url = (
                f"https://api.themoviedb.org/3/{endpoint}?api_key={API_KEY}&page={page}"
            )
            logger.info(f"Fetching category={category}, page={page}")

            response = requests.get(url)

            if response.status_code != 200:
                logger.warning(
                    f"API request failed for {category}, page {page}: {response.status_code}"
                )
                continue

            data = response.json()

            for movie in data.get("results", []):
                valid, reason = is_valid_movie(movie)

                if not valid:
                    total_skipped += 1
                    logger.warning(f"Skipped movie record: {reason}")
                    continue

                cursor.execute(
                    """
                INSERT OR IGNORE INTO movies
                (movie_id, date, title, rating, votes, release_date, popularity, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        movie.get("id"),
                        today,
                        movie.get("title"),
                        movie.get("vote_average"),
                        movie.get("vote_count"),
                        movie.get("release_date"),
                        movie.get("popularity"),
                        category,
                    ),
                )

                total_inserted += 1

    conn.commit()
    conn.close()

    logger.info(
        f"Movie ingestion completed successfully. Inserted={total_inserted}, Skipped={total_skipped}"
    )
    print("Movie database updated successfully.")


if __name__ == "__main__":
    main()
