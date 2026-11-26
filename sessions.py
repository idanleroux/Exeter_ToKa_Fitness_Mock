import sqlite3
import secrets
import hashlib
import time
from functools import wraps
from flask import request, make_response, redirect, url_for, g

DATABASE = "database.db" # CHANGE to your database path
COOKIE_NAME = "session_token"
SESSION_DURATION = 7 * 24 * 60 * 60 # 7 days

# Database connection
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
        FOREIGN KEY(user_id) REFERENCES users(id) ON
    DELETE CASCADE
    )
    """)
    db.commit()
    db.close()

# Create a new server-side session
def create_session(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires = int(time.time()) + SESSION_DURATION
    db = get_db()
    db.execute(
    "INSERT INTO sessions (token_hash, user_id, expires_at)VALUES (?, ?, ?)",
    (token_hash, user_id, expires)
    )
    db.commit()
    db.close()
    response = make_response(redirect(url_for("index")))
    response.set_cookie(
    COOKIE_NAME,
    token,
    max_age=SESSION_DURATION,
    httponly=True,
    secure=True, # HTTPS required in production
    samesite="Lax",
    path="/"
    )
    return response

# Retrieve and validate the current session
def get_session():
    token = request.cookies.get(COOKIE_NAME)
    if not token:
     return None
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db = get_db()
    user = db.execute("""
    SELECT users.id, users.is_premium
    FROM sessions
    JOIN users ON users.id = sessions.user_id
    WHERE sessions.token_hash = ?
    AND sessions.expires_at > ?
    """, (token_hash, int(time.time()))).fetchone()
    # Remove expired session if necessary
    db.execute("DELETE FROM sessions WHERE expires_at <=?", (int(time.time()),))
    db.commit()
    db.close()
    return user

# Make login information available to Flask routes/templates
def load_user():
    g.user = get_session()
# Require login for protected routes
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(g, "user", None):
            return redirect(url_for("login"))
            return func(*args, **kwargs)
            return wrapper

# Require premium membership
def premium_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "user", None)
        if not user:
            return redirect(url_for("login"))
        if not user["is_premium"]:
            return "Premium membership required", 403
        return func(*args, **kwargs)
    return wrapper

# Destroy current session
def destroy_session():
    token = request.cookies.get(COOKIE_NAME)
    if token:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db = get_db()
        db.execute(
            "DELETE FROM sessions WHERE token_hash = ?",
            (token_hash,)
        )
        db.commit()
        db.close()
    response = make_response(redirect(url_for("login")))
    response.delete_cookie(COOKIE_NAME, path="/", secure=True, httponly=True, samesite="Lax")
    return response