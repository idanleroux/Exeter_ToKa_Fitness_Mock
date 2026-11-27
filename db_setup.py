import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

def db_make():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(64) UNIQUE,
            password VARCHAR(64) NOT NULL,
            account_type VARCHAR(64) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            post_title VARCHAR(64) NOT NULL,
            post_description VARCHAR(64) NOT NULL,
            post_image VARCHAR(256) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pt_sessions (
            user_id INTEGER PRIMARY KEY,
            time TIMESTAMP NOT NULL,
            location VARCHAR(64) NOT NULL,
            activity VARCHAR(64) NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def db_seed():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (email, password, account_type)
        VALUES (?, ?, ?)
    """, ("test@test.com", "1234", "premium"))

    conn.commit()
    conn.close()

def do_both():
    db_make()
    db_seed()

if __name__ == "__main__":
    do_both()