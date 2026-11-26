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

app = Flask(__name__)
app.secret_key = "YOUR_LONG_RANDOM_SECRET_KEY"

# Protect POST requests against CSRF
CSRFProtect(app)

# Create session table
init_sessions()

def get_meal_plan(calorie, protein, diet):
    if calorie == "high":
        print("")

def is_logged_in():
    #if session["logged_in"] is True:
        #return True
    #else:
        #return False
    return True

# Load current user on every request
@app.before_request
def before_request():
    load_user()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/workouts")
def workouts():
    return render_template("L_workouts.html")

@app.route("/sessions")
def sessions():
    return render_template("P_pt_sessions.html")


@app.route("/diets", methods=["GET", "POST"])
def diets():

    if not is_logged_in():
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
    return render_template("P_community.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check credentials (you'll replace this with your own logic)
        if request.form["email"] == "admin" and request.form["password"] == "password":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "Invalid email/password combination"
    return render_template("login.html")

@app.route("/logout")
def logout():
    # Remove all keys from the session dictionary
    session.clear()
    return redirect(url_for("login"))


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