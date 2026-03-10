import sqlite3

conn = sqlite3.connect("auditions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS auditions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    show TEXT,
    feedback TEXT
)
""")

conn.commit()
