import sqlite3
import os
from flask import Flask, g, render_template, redirect, url_for, request, session
from flask_wtf.csrf import CSRFProtect
from sessions import (
    init_sessions,
    load_user,
    create_session,
    destroy_session,
    login_required,
    premium_required
)

from db_setup import do_both
do_both()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = "YOUR_LONG_RANDOM_SECRET_KEY"

# Create session table
init_sessions()

def check_email(user_email, user_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    result = cursor.execute(
        "SELECT password FROM users WHERE email = ?",
        (user_email,)
    ).fetchone()

    conn.close()

    if result and result[0] == user_password:
        session["logged_in"] = True
        return True

    return False

def check_premium(user_email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    result = cursor.execute(
        "SELECT account_type FROM users WHERE email = ?",
        (user_email,)
    ).fetchone()

    conn.close()

    if result and result[0] == "premium":
        session["is_premium"] = True
        return True

    return False


def get_meal_plan(calorie, protein, diet):
    if calorie == "high":
        print("")

# Load current user on every request
@app.before_request
def before_request():
    load_user()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/workouts")
def workouts():

    if session["logged_in"] is not True:
        return redirect(url_for("login"))
    return render_template("L_workouts.html")

@app.route("/sessions")
def sessions():

    if session["logged_in"] is not True:
        return redirect(url_for("login"))
    return render_template("P_pt_sessions.html")


@app.route("/diets", methods=["GET", "POST"])
def diets():

    if session["logged_in"] is not True:
        return redirect(url_for("login"))

    meal_plan = None

    if request.method == "POST":
        calorie = request.form.get("calorie")
        protein = request.form.get("protein")
        diet = request.form.get("diet")

        meal_plan = get_meal_plan(calorie, protein, diet)

    return render_template("L_diets.html", meal_plan=meal_plan)

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")

@app.route("/community")
def community():

    if session["logged_in"] is not True:
        return redirect(url_for("login"))

    return render_template("P_community.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if session.get("logged_in"):
            return redirect(url_for("logout"))
        if check_email(request.form["email"], request.form["password"]) is True:
            print("#################### Login Successful! ####################")
            check_premium()
            return redirect(url_for("index"))
        print("#################### Something went wrong, probably bad email/password combination ####################")
        return render_template("login.html")
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        # Remove all keys from the session dictionary
        session.clear()
        return redirect(url_for("login"))
    return render_template("logout.html")

if __name__ == "__main__":
    app.run()