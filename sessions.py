import sqlite3
import os
import secrets
import hashlib
import time

from flask import (
    request,
    g,
    make_response,
    redirect,
    url_for
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

COOKIE_NAME = "auth_token"
SESSION_DURATION = 86400


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Run once when your application starts
def init_sessions():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            FOREIGN KEY(user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()

# Create a new server-side session
def create_session(user_id):
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    expires = int(time.time()) + SESSION_DURATION
    db = get_db()

    db.execute("""
        INSERT INTO sessions
        (token_hash, user_id, expires_at)
        VALUES (?, ?, ?)
    """, (token_hash, user_id, expires))

    db.commit()
    db.close()

    response = make_response(
        redirect(url_for("index"))
    )

    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=SESSION_DURATION,
        httponly=True,
        secure=False,  # True when deployed with HTTPS
        samesite="Lax",
        path="/"
    )

    return response


# Retrieve and validate the current session
def get_session():
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    db = get_db()

    user = db.execute("""
        SELECT
            users.user_id,
            users.email,
            users.account_type
        FROM sessions
        JOIN users
            ON users.user_id = sessions.user_id
        WHERE sessions.token_hash = ?
        AND sessions.expires_at > ?
    """, (token_hash, int(time.time()))).fetchone()

    # Remove expired sessions
    db.execute("""
        DELETE FROM sessions
        WHERE expires_at <= ?
    """, (int(time.time()),))

    db.commit()
    db.close()

    return user


# Make user available to Flask routes
def load_user():
    g.user = get_session()


# Destroy current session
def destroy_session():
    token = request.cookies.get(COOKIE_NAME)

    if token:
        token_hash = hashlib.sha256(
            token.encode()
        ).hexdigest()

        db = get_db()

        db.execute("""
            DELETE FROM sessions
            WHERE token_hash = ?
        """, (token_hash,))

        db.commit()
        db.close()