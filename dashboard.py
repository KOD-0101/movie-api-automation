import os
import sqlite3
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# -----------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------
load_dotenv()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Movie Data Automation Project",
    layout="wide"
)

# -----------------------------
# API KEY
# Try Streamlit secrets first, then .env
# -----------------------------
TMDB_API_KEY = None

try:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movies.db")

# -----------------------------
# PAGE STATE
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def go_to_dashboard():
    st.session_state.page = "dashboard"


def get_local_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    return df


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY not found in Streamlit secrets or .env")

    url = f"https://api.themoviedb.org/3/{endpoint}"
    query = {"api_key": TMDB_API_KEY}

    if params:
        query.update(params)

    response = requests.get(url, params=query, timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600)
def get_genres() -> list[dict]:
    data = tmdb_get("genre/movie/list")
    return data.get("genres", [])


@st.cache_data(ttl=1800)
def get_movies_by_genre(genre_id: int, pages: int = 2) -> list[dict]:
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

    return movies


@st.cache_data(ttl=1800)
def get_movie_details(movie_id: int) -> dict:
    return tmdb_get(f"movie/{movie_id}")


def poster_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"https://image.tmdb.org/t/p/w500{path}"


# -----------------------------
# HOME PAGE
# -----------------------------
if st.session_state.page == "home":
    st.title("🎬 Movie Data Automation Project")

    st.image(
        "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4",
        width="stretch"
    )

    st.markdown("---")

    st.markdown(
        """
        ### Welcome

        This application demonstrates a complete automated movie data workflow.

        #### Features
        - 📡 Automated movie data collection from the TMDB API
        - 🗄️ SQLite database storage
        - 📊 Data analysis using Python and SQL
        - 📈 Interactive charts and dashboard insights
        - 🎭 Genre-based movie recommendations
        - 🎥 Movie summaries and details
        """
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.button("🚀 Get Started", on_click=go_to_dashboard,
                  use_container_width=True)

    st.markdown("---")
    st.markdown("Built with Python, Streamlit, SQLite, and TMDB API")

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
elif st.session_state.page == "dashboard":
    st.title("📊 Movie Dashboard")

    # -----------------------------
    # LOCAL DATABASE ANALYTICS
    # -----------------------------
    try:
        df = get_local_data()

        if df.empty:
            st.warning("No local database records found.")
        else:
            # Search
            st.subheader("🔎 Search Local Database")
            search = st.text_input("Enter movie title")

            if search:
                results = df[df["title"].str.contains(
                    search, case=False, na=False)]
                st.dataframe(results, use_container_width=True)

            # Top rated and most popular tables
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("⭐ Top Rated Movies")
                top_movies = df.sort_values(
                    by="rating", ascending=False).head(10)
                st.dataframe(
                    top_movies[["title", "rating", "release_date"]],
                    use_container_width=True
                )

            with col2:
                st.subheader("🔥 Most Popular Movies")
                popular = df.sort_values(
                    by="popularity", ascending=False).head(10)
                st.dataframe(
                    popular[["title", "popularity"]],
                    use_container_width=True
                )

            # Average rating
            st.subheader("📊 Average Rating")
            st.write(round(df["rating"].mean(), 2))

            # Charts
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.subheader("📈 Rating Distribution")
                fig, ax = plt.subplots()
                df["rating"].hist(bins=10, ax=ax)
                ax.set_xlabel("Rating")
                ax.set_ylabel("Frequency")
                st.pyplot(fig)

            with chart_col2:
                st.subheader("📊 Top 10 Most Popular Movies")
                top_popular = df.sort_values(
                    by="popularity", ascending=False).head(10)
                fig2, ax2 = plt.subplots()
                ax2.barh(top_popular["title"], top_popular["popularity"])
                ax2.set_xlabel("Popularity Score")
                ax2.set_ylabel("Movie Title")
                ax2.invert_yaxis()
                st.pyplot(fig2)

    except Exception as e:
        st.error(f"Local database section failed: {e}")

    st.markdown("---")

    # -----------------------------
    # GENRE-BASED RECOMMENDATIONS
    # -----------------------------
    st.header("🎭 Genre-Based Recommendations")

    if not TMDB_API_KEY:
        st.warning("TMDB live recommendation features need a TMDB_API_KEY.")
    else:
        try:
            genres = get_genres()
            genre_names = [g["name"] for g in genres]
            genre_map = {g["name"]: g["id"] for g in genres}

            selected_genre_name = st.selectbox(
                "Choose a genre",
                genre_names,
                index=genre_names.index(
                    "Horror") if "Horror" in genre_names else 0
            )

            selected_genre_id = genre_map[selected_genre_name]
            genre_movies = get_movies_by_genre(selected_genre_id, pages=2)

            if not genre_movies:
                st.info("No movies found for this genre.")
            else:
                st.subheader(f"Recommended {selected_genre_name} Movies")

                # Show first 12 movies as cards
                genre_movies = genre_movies[:12]
                cols = st.columns(3)

                for i, movie in enumerate(genre_movies):
                    with cols[i % 3]:
                        poster = poster_url(movie.get("poster_path"))

                        if poster:
                            st.image(poster, width="stretch")
                        else:
                            st.write("No poster available")

                        st.markdown(
                            f"**{movie.get('title', 'Unknown Title')}**")

                        release_date = movie.get("release_date", "")
                        year = release_date[:4] if release_date else "N/A"

                        st.write(f"Year: {year}")
                        st.write(f"Rating: {movie.get('vote_average', 'N/A')}")

                        if st.button("View Details", key=f"movie_{movie['id']}"):
                            st.session_state.selected_movie_id = movie["id"]

                # Movie details section
                if st.session_state.selected_movie_id:
                    details = get_movie_details(
                        st.session_state.selected_movie_id)

                    st.markdown("---")
                    st.header("🎥 Movie Details")

                    detail_col1, detail_col2 = st.columns([1, 2])

                    with detail_col1:
                        poster = poster_url(details.get("poster_path"))
                        if poster:
                            st.image(poster, width="stretch")

                    with detail_col2:
                        st.subheader(details.get("title", "Unknown Title"))
                        st.markdown(
                            f"**Release Date:** {details.get('release_date', 'N/A')}")
                        st.markdown(
                            f"**Rating:** {details.get('vote_average', 'N/A')}")
                        st.markdown(
                            f"**Votes:** {details.get('vote_count', 'N/A')}")
                        st.markdown(
                            f"**Popularity:** {details.get('popularity', 'N/A')}")

                        runtime = details.get("runtime")
                        if runtime:
                            st.markdown(f"**Runtime:** {runtime} minutes")

                        genres = details.get("genres", [])
                        if genres:
                            genre_list = ", ".join(g["name"] for g in genres)
                            st.markdown(f"**Genres:** {genre_list}")

                        st.markdown("**Summary:**")
                        st.write(details.get(
                            "overview", "No summary available."))

        except Exception as e:
            st.error(f"Genre recommendation section failed: {e}")
