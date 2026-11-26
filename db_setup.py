import sqlite3
def db_make():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Add users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id int PRIMARY KEY,
        email varchar(64) UNIQUE,
        password varchar(64) NOT NULL,
        account_type varchar(64) NOT NULL)
    """)

    # Add community posts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_posts (
    post_title varchar(64) NOT NULL,
    post_description varchar(64) NOT NULL,
    post_image varchar(256) NOT NULL)
    """)

    # Add pt sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pt_sessions
    (user_id imt PRIMARY KEY,
    time timestamp NOT NULL,
    location varchar(64) NOT NULL,
    activity varchar(64) NOT NULL)
    """)
    conn.commit()
    conn.close()

def db_seed():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Add set of test users
    cursor.execute("""
    INSERT INTO users (
        test@test.com,
        1234,
        free)
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_make()
    db_seed()