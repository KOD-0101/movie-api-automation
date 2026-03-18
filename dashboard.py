import streamlit as st
import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt

# find database path automatically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "movies.db")

# connect to database
conn = sqlite3.connect(db_path)

df = pd.read_sql_query("SELECT * FROM movies", conn)

st.title("🎬 Movie Data Dashboard")

# -------------------------------
# SEARCH FEATURE
# -------------------------------

st.subheader("🔎 Search for a Movie")

movie_search = st.text_input("Enter movie title")

if movie_search:
    results = df[df["title"].str.contains(movie_search, case=False)]
    st.dataframe(results)

# -------------------------------
# TOP RATED MOVIES
# -------------------------------

st.subheader("⭐ Top Rated Movies")

top_movies = df.sort_values(by="rating", ascending=False).head(10)

st.dataframe(top_movies[["title", "rating", "release_date"]])

# -------------------------------
# MOST POPULAR MOVIES
# -------------------------------

st.subheader("🔥 Most Popular Movies")

popular_movies = df.sort_values(by="popularity", ascending=False).head(10)

st.dataframe(popular_movies[["title", "popularity"]])

# -------------------------------
# AVERAGE RATING
# -------------------------------

st.subheader("📊 Average Rating")

st.write(round(df["rating"].mean(), 2))

# -------------------------------
# RATING DISTRIBUTION CHART
# -------------------------------

st.subheader("📈 Movie Rating Distribution")

fig, ax = plt.subplots()
df["rating"].hist(bins=10, ax=ax)

st.pyplot(fig)

# -------------------------------
# TOP 10 POPULARITY CHART
# -------------------------------

st.subheader("📊 Top 10 Most Popular Movies")

top_popular = df.sort_values(by="popularity", ascending=False).head(10)

fig, ax = plt.subplots()

ax.barh(top_popular["title"], top_popular["popularity"])

ax.set_xlabel("Popularity Score")
ax.set_ylabel("Movie Title")

ax.invert_yaxis()

st.pyplot(fig)
