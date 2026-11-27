import sqlite3
import os

from flask import (
    Flask,
    g,
    render_template,
    redirect,
    url_for,
    request,
    make_response
)

from sessions import (
    init_sessions,
    load_user,
    create_session,
    destroy_session,
    COOKIE_NAME
)

from db_setup import do_both, DATABASE

# Initialise database
do_both()

app = Flask(__name__)

app.secret_key = "YOUR_LONG_RANDOM_SECRET_KEY"

# Initialise server-side sessions table
init_sessions()

# Check login details
def check_email(user_email, user_password):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    user = conn.execute("""
        SELECT user_id, password
        FROM users
        WHERE email = ?
    """, (user_email,)).fetchone()

    conn.close()

    if user and user["password"] == user_password:
        return user["user_id"]

    return None

# Load current user on every request
@app.before_request
def before_request():
    load_user()

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Workouts
@app.route("/workouts")
def workouts():

    if g.user is None:
        return redirect(url_for("login"))

    return render_template("L_workouts.html")

# Premium PT sessions
@app.route("/sessions")
def sessions():

    if g.user is None:
        return redirect(url_for("login"))

    if g.user["account_type"] != "premium":
        return redirect(url_for("premium_required"))

    return render_template("P_pt_sessions.html")

# Diets
@app.route("/diets", methods=["GET", "POST"])
def diets():

    if g.user is None:
        return redirect(url_for("login"))

    meal_plan = None
    if request.method == "POST":
        calorie = request.form.get("calorie")
        protein = request.form.get("protein")
        diet_type = request.form.get("diet")
        if not all([calorie, protein, diet_type]):
            return "Please select all three options", 400
        code = get_meal_plan(calorie, protein, diet_type)
        results = get_meals(code)
        return render_template("L_diets.html", results=results)

    return render_template("login.html")

# Meal plan function
def get_meal_plan(calorie, protein, diet):
    if calorie == "high":
        if protein == "high":
            if diet == "vegan":
                return "HHv"
            if diet == "vegetarian":
                return "HHV"
            if diet == "omnivore":
                return "HHO"
            return "HHP"
        if diet == "vegan":
            return "HRv"
        if diet == "vegetarian":
            return "HRV"
        if diet == "omnivore":
            return "HRO"
        return "HRP"
    if protein == "high":
        if diet == "vegan":
            return "LHv"
        if diet == "vegetarian":
            return "LHV"
        if diet == "omnivore":
            return "LHO"
        return "LHP"
    if diet == "vegan":
        return "LRv"
    if diet == "vegetarian":
        return "LRV"
    if diet == "omnivore":
        return "LRO"
    return "LRP"

def get_meals(code):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    rtn = conn.execute("""
                        SELECT meals
                        FROM diet
                        WHERE code = ?
                        """)
    conn.close()
    return rtn

# Navbar
@app.route("/navbar")
def navbar():
    return render_template("navbar.html")

@app.route("/advice")
def advice():
    return render_template("advice.html")

# Community
@app.route("/community")
def community():

    if g.user is None:
        return redirect(url_for("login"))

    if g.user["account_type"] != "premium":
        return redirect(url_for("premium_required"))

    return render_template("P_community.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = check_email(
            request.form["email"],
            request.form["password"]
        )
        if user_id is not None:
            print("#################### LOGIN SUCCESSFUL ####################")
            return create_session(user_id)
        print("#################### LOGIN FAILED ####################")
        return render_template("login.html")
    return render_template("login.html")


# Premium required
@app.route("/premium-required")
def premium_required():
    if g.user is None:
        return redirect(url_for("login"))
    return render_template("premium_required.html")

# Logout
@app.route("/logout", methods=["GET", "POST"])
def logout():

    if request.method == "POST":
        destroy_session()

        response = make_response(
            redirect(url_for("login"))
        )
        response.delete_cookie(
            COOKIE_NAME,
            path="/"
        )
        return response
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)