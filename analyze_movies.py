import sqlite3

# connect to database
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

print("\nTop 10 Highest Rated Movies:\n")

cursor.execute("""
SELECT title, rating
FROM movies
ORDER BY rating DESC
LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

print("\nMost Popular Movies:\n")

cursor.execute("""
SELECT title, popularity
FROM movies
ORDER BY popularity DESC
LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

print("\nAverage Movie Rating:\n")

cursor.execute("""
SELECT AVG(rating)
FROM movies
""")

print(cursor.fetchone()[0])

conn.close()
