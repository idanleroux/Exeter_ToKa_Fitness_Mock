from flask import Flask, g, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from sessions import (
    init_sessions,
    load_user,
    create_session,
    destroy_session,
    login_required,
    premium_required
)

app = Flask(__name__)
app.secret_key = "YOUR_LONG_RANDOM_SECRET_KEY"

# Protect POST requests against CSRF
CSRFProtect(app)

# Create session table
init_sessions()

# Load current user on every request
@app.before_request
def before_request():
    load_user()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/L_diets")
def diets():
    return render_template("diets.html")

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")

@app.route("/community")
def community():
    return render_template("P_community.html")

"""
@app.route("/login", methods=["GET", "POST"])
def login():
    # INTEGRATE YOUR EXISTING LOGIN / PASSWORD VERIFICATION HERE.
    #
    # Once credentials have been successfully verified:
    #
     # return create_session(user_id)
    return render_template("login.html")

@app.route("/L_logout", methods=["POST"])
@login_required
def logout():
    return destroy_session()

@app.route("/L_diets")
@login_required
def diets():
    return "You are logged in!"

@app.route("/community")
@premium_required
def community():
    return "Welcome, premium member!"
"""

if __name__ == "__main__":
    app.run()