import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from database import get_connection, init_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-admission-key")

# Run database setup on start
init_db()

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user["password"], password):
                session["user"] = user["username"]
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password.", "error")
        except Exception as e:
            flash(f"Database error: {e}", "error")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id DESC")
        students = cursor.fetchall()
        conn.close()
    except Exception as e:
        students = []
        flash(f"Could not load students: {e}", "error")

    return render_template("dashboard.html", user=session["user"], students=students)

@app.route("/add_student", methods=["POST"])
def add_student():
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    course = request.form.get("course")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email, phone, course) VALUES (?, ?, ?, ?)",
            (name, email, phone, course)
        )
        conn.commit()
        conn.close()
        flash("Student added successfully!", "success")
    except Exception as e:
        flash(f"Failed to add student: {e}", "error")

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)