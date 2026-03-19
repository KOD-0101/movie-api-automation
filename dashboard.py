import streamlit as st
import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt

# -----------------------------
# Page Navigation Setup
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"


def go_to_dashboard():
    st.session_state.page = "dashboard"


# -----------------------------
# HOME PAGE (Landing Page)
# -----------------------------
if st.session_state.page == "home":

    st.title("🎬 Movie Data Automation Project")

    st.markdown("""
    ### Welcome!

    This application automatically collects movie data using an API,
    stores it in a database, and provides insights through a dashboard.

    #### Features:
    - 📡 Automated data collection
    - 🗄️ Database storage (SQLite)
    - 📊 Data analysis
    - 📈 Interactive visualisations
    """)

    st.button("🚀 Get Started", on_click=go_to_dashboard)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
elif st.session_state.page == "dashboard":

    st.title("📊 Movie Dashboard")

    # Database path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "movies.db")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    # Load data
    df = pd.read_sql_query("SELECT * FROM movies", conn)

    if df.empty:
        st.warning("No data available. Run the data collection script.")
    else:
        # 🔎 Search
        st.subheader("🔎 Search for a Movie")
        search = st.text_input("Enter movie title")

        if search:
            results = df[df["title"].str.contains(
                search, case=False, na=False)]
            st.dataframe(results)

        # ⭐ Top Rated
        st.subheader("⭐ Top Rated Movies")
        top_movies = df.sort_values(by="rating", ascending=False).head(10)
        st.dataframe(top_movies[["title", "rating", "release_date"]])

        # 🔥 Popular
        st.subheader("🔥 Most Popular Movies")
        popular = df.sort_values(by="popularity", ascending=False).head(10)
        st.dataframe(popular[["title", "popularity"]])

        # 📊 Average
        st.subheader("📊 Average Rating")
        st.write(round(df["rating"].mean(), 2))

        # 📈 Rating Distribution
        st.subheader("📈 Rating Distribution")
        fig, ax = plt.subplots()
        df["rating"].hist(bins=10, ax=ax)
        st.pyplot(fig)

    conn.close()
