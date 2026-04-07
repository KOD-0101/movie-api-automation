import os
import requests
import streamlit as st
from dotenv import load_dotenv
from logger_setup import get_logger

load_dotenv()
logger = get_logger("api")

TMDB_API_KEY = None

try:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
    logger.info("TMDB API key loaded from Streamlit secrets")
except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    if TMDB_API_KEY:
        logger.info("TMDB API key loaded from .env")
    else:
        logger.warning("TMDB API key could not be found")


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    if not TMDB_API_KEY:
        logger.error("TMDB_API_KEY not found")
        raise ValueError("TMDB_API_KEY not found in Streamlit secrets or .env")

    url = f"https://api.themoviedb.org/3/{endpoint}"
    query = {"api_key": TMDB_API_KEY}

    if params:
        query.update(params)

    logger.info(f"Calling TMDB endpoint: {endpoint}")
    response = requests.get(url, params=query, timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600)
def get_genres() -> list[dict]:
    logger.info("Fetching movie genres")
    data = tmdb_get("genre/movie/list")
    return data.get("genres", [])


@st.cache_data(ttl=1800)
def get_movies_by_genre(genre_id: int, pages: int = 2) -> list[dict]:
    logger.info(f"Fetching movies for genre_id={genre_id}, pages={pages}")
    movies = []

    for page in range(1, pages + 1):
        data = tmdb_get(
            "discover/movie",
            {
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "page": page,
            },
        )
        movies.extend(data.get("results", []))

    logger.info(f"Fetched {len(movies)} movies for genre_id={genre_id}")
    return movies


@st.cache_data(ttl=1800)
def get_movie_details(movie_id: int) -> dict:
    logger.info(f"Fetching details for movie_id={movie_id}")
    return tmdb_get(f"movie/{movie_id}")
