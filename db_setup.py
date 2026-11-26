import sqlite3
def db_seed():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Add users
    cursor.execute("""
    INSERT INTO users (user_id, email, password, account_type)
    VALUES (?, ?, ?, ?)
    """, (1, "admin@example.com", "hashed_password_here",
    "premium"))

    # Add community posts
    cursor.execute("""
    INSERT INTO community_posts
    (post_title, post_description, post_image)
    VALUES (?, ?, ?)
    """, ("Welcome!", "Welcome to the community.", None, 0, "[]",
    1))

    # Add pt sessions
    cursor.execute("""
    INSERT INTO pt_sessions
    (user_id, time, location, activity)
    VALUES (?, ?, ?, ?)
    """, (1, "2026-11-23 12:00:00", "Gym one", "Getting started"))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_seed()