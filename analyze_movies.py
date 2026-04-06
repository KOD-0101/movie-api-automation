import requests
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from logger_setup import get_logger

load_dotenv()
logger = get_logger("get_top_movies")

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    logger.error("API key not found")
    print("Error: API key not found.")
    exit()

today = datetime.today().strftime("%Y-%m-%d")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movies.db")

logger.info("Movie ingestion started")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    date TEXT,
    title TEXT,
    rating REAL,
    votes INTEGER,
    release_date TEXT,
    popularity REAL
)
""")

logger.info("Database connection established and table checked")

total_inserted = 0

for page in range(1, 6):
    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&page={page}"
    logger.info(f"Fetching page {page} from TMDB API")

    response = requests.get(url)

    if response.status_code != 200:
        logger.warning(
            f"API request failed on page {page}: {response.status_code}")
        print("API request failed:", response.status_code)
        conn.close()
        exit()

    data = response.json()

    for movie in data.get("results", []):
        cursor.execute("""
        INSERT INTO movies (date, title, rating, votes, release_date, popularity)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            today,
            movie.get("title"),
            movie.get("vote_average"),
            movie.get("vote_count"),
            movie.get("release_date"),
            movie.get("popularity")
        ))
        total_inserted += 1

conn.commit()
conn.close()

logger.info(
    f"Movie ingestion completed successfully. Inserted {total_inserted} records.")
print("Movie database updated successfully.")
