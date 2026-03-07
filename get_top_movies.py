import requests
import os
import csv
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}"

response = requests.get(url)
data = response.json()

print("\nTop Rated Movies:\n")

movies = data["results"][:5]

for movie in movies:
    print(movie["title"], "⭐", movie["vote_average"])


# Save to CSV
with open("top_movies.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # header
    writer.writerow(["Title", "Rating", "Release Date"])

    # rows
    for movie in movies:
        writer.writerow([
            movie["title"],
            movie["vote_average"],
            movie["release_date"]
        ])

print("\nMovies saved to top_movies.csv")
