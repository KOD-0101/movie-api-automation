import requests
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    print("Error: API key not found.")
    exit()

today = datetime.today().strftime("%Y-%m-%d")

# Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

# Create table if it doesn't exist
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

# Collect movies
for page in range(1, 6):

    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&page={page}"

    response = requests.get(url)

    if response.status_code != 200:
        print("API request failed:", response.status_code)
        exit()

    data = response.json()

    for movie in data["results"]:

        cursor.execute("""
        INSERT INTO movies (date,title,rating,votes,release_date,popularity)
        VALUES (?,?,?,?,?,?)
        """, (
            today,
            movie.get("title"),
            movie.get("vote_average"),
            movie.get("vote_count"),
            movie.get("release_date"),
            movie.get("popularity")
        ))

# Save changes
conn.commit()
conn.close()

print("Movie database updated successfully.")
