import streamlit as st
import matplotlib.pyplot as plt
from logger_setup import get_logger
from database import get_local_data
from api import get_genres, get_movies_by_genre, get_movie_details, TMDB_API_KEY
from ui_helpers import poster_url, go_to_dashboard

logger = get_logger("dashboard")


def render_home_page():
    logger.info("Rendering home page")

    st.title("🎬 Movie Data Automation Project")

    st.image("https://images.unsplash.com/photo-1524985069026-dd778a71c7b4", width=500)

    st.markdown("---")

    st.markdown("""
        ### Welcome

        This application demonstrates a complete automated movie data workflow.

        #### Features
        - 📡 Automated movie data collection from the TMDB API
        - 🗄️ SQLite database storage
        - 📊 Data analysis using Python and SQL
        - 📈 Interactive charts and dashboard insights
        - 🎭 Genre-based movie recommendations
        - 🎥 Movie summaries and details
        """)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.button("🚀 Get Started", on_click=go_to_dashboard, use_container_width=True)

    st.markdown("---")
    st.markdown("Built with Python, Streamlit, SQLite, and TMDB API")


def render_local_analytics():
    logger.info("Rendering local analytics section")

    try:
        df = get_local_data()

        if df.empty:
            logger.warning("No local database records found")
            st.warning("No local database records found.")
            return

        st.subheader("🔎 Search Local Database")
        search = st.text_input("Enter movie title")

        if search:
            logger.info(f"User searched local database for: {search}")
            results = df[df["title"].str.contains(search, case=False, na=False)]
            st.dataframe(results, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⭐ Top Rated Movies")
            top_movies = df.sort_values(by="rating", ascending=False).head(10).copy()
            top_movies["rating"] = top_movies["rating"].round(1)
            st.dataframe(
                top_movies[["title", "rating", "release_date"]],
                use_container_width=True,
            )

        with col2:
            st.subheader("🔥 Most Popular Movies")
            popular = df.sort_values(by="popularity", ascending=False).head(10).copy()
            popular["popularity"] = popular["popularity"].round(0).astype(int)
            st.dataframe(popular[["title", "popularity"]], use_container_width=True)

        st.subheader("📊 Average Rating")
        st.write(round(df["rating"].mean(), 2))

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
            top_popular = df.sort_values(by="popularity", ascending=False).head(10)
            fig2, ax2 = plt.subplots()
            ax2.barh(top_popular["title"], top_popular["popularity"])
            ax2.set_xlabel("Popularity Score")
            ax2.set_ylabel("Movie Title")
            ax2.invert_yaxis()
            st.pyplot(fig2)

    except Exception:
        logger.exception("Local database section failed")
        st.error("Local database section failed.")


def render_genre_recommendations():
    logger.info("Rendering genre recommendation section")

    st.header("🎭 Genre-Based Recommendations")

    if not TMDB_API_KEY:
        logger.warning(
            "TMDB live recommendation features unavailable due to missing API key"
        )
        st.warning("TMDB live recommendation features need a TMDB_API_KEY.")
        return

    try:
        genres = get_genres()
        genre_names = [g["name"] for g in genres]
        genre_map = {g["name"]: g["id"] for g in genres}

        selected_genre_name = st.selectbox(
            "Choose a genre",
            genre_names,
            index=genre_names.index("Horror") if "Horror" in genre_names else 0,
        )

        logger.info(f"Selected genre: {selected_genre_name}")

        selected_genre_id = genre_map[selected_genre_name]
        genre_movies = get_movies_by_genre(selected_genre_id, pages=2)

        if not genre_movies:
            logger.warning(f"No movies found for genre: {selected_genre_name}")
            st.info("No movies found for this genre.")
            return

        st.subheader(f"Recommended {selected_genre_name} Movies")

        genre_movies = genre_movies[:12]
        cols = st.columns(3)

        for i, movie in enumerate(genre_movies):
            with cols[i % 3]:
                poster = poster_url(movie.get("poster_path"))

                if poster:
                    st.image(poster, width="stretch")
                else:
                    st.write("No poster available")

                st.markdown(f"**{movie.get('title', 'Unknown Title')}**")

                release_date = movie.get("release_date", "")
                year = release_date[:4] if release_date else "N/A"

                st.write(f"Year: {year}")
                st.write(f"Rating: {movie.get('vote_average', 'N/A')}")

                if st.button("View Details", key=f"movie_{movie['id']}"):
                    st.session_state.selected_movie_id = movie["id"]
                    logger.info(f"Selected movie details for movie_id={movie['id']}")

        if st.session_state.selected_movie_id:
            details = get_movie_details(st.session_state.selected_movie_id)

            st.markdown("---")
            st.header("🎥 Movie Details")

            detail_col1, detail_col2 = st.columns([1, 2])

            with detail_col1:
                poster = poster_url(details.get("poster_path"))
                if poster:
                    st.image(poster, width="stretch")

            with detail_col2:
                st.subheader(details.get("title", "Unknown Title"))
                st.markdown(f"**Release Date:** {details.get('release_date', 'N/A')}")
                st.markdown(f"**Rating:** {details.get('vote_average', 'N/A')}")
                st.markdown(f"**Votes:** {details.get('vote_count', 'N/A')}")
                st.markdown(f"**Popularity:** {details.get('popularity', 'N/A')}")

                runtime = details.get("runtime")
                if runtime:
                    st.markdown(f"**Runtime:** {runtime} minutes")

                genres = details.get("genres", [])
                if genres:
                    genre_list = ", ".join(g["name"] for g in genres)
                    st.markdown(f"**Genres:** {genre_list}")

                st.markdown("**Summary:**")
                st.write(details.get("overview", "No summary available."))

    except Exception:
        logger.exception("Genre recommendation section failed")
        st.error("Genre recommendation section failed.")


def render_dashboard_page():
    logger.info("Rendering dashboard page")
    st.title("📊 Movie Dashboard")
    render_local_analytics()
    st.markdown("---")
    render_genre_recommendations()
