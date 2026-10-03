import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from database import get_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_dev_key")

@app.route("/", methods=["GET", "POST"], strict_slashes=False)
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            con.close()

            if user and check_password_hash(user["password_hash"], password):
                session["user"] = user["username"]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password.", "danger")
        except Exception as e:
            flash(f"Database error: {e}", "danger")

    return render_template("login.html")

@app.route("/logout", strict_slashes=False)
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard", strict_slashes=False)
def dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    search_query = request.args.get("search", "").strip()
    students = []

    try:
        con = get_connection()
        cur = con.cursor(dictionary=True)

        if search_query:
            query = """SELECT * FROM student 
                       WHERE name LIKE %s OR branch LIKE %s OR email LIKE %s 
                       ORDER BY id DESC"""
            cur.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        else:
            cur.execute("SELECT * FROM student ORDER BY id DESC")

        students = cur.fetchall()
        cur.close()
        con.close()
    except Exception as e:
        flash(f"Error fetching records: {e}", "danger")

    return render_template("dashboard.html", students=students, search_query=search_query)

@app.route("/student/insert", methods=["POST"], strict_slashes=False)
def insert_student():
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    age = request.form.get("age")
    branch = request.form.get("branch", "").strip()
    address = request.form.get("address", "").strip()
    email = request.form.get("email", "").strip()

    try:
        con = get_connection()
        cur = con.cursor()
        query = "INSERT INTO student (name, age, branch, address, email) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(query, (name, age, branch, address, email))
        con.commit()
        cur.close()
        con.close()
        flash("Student added successfully!", "success")
    except Exception as e:
        flash(f"Error adding student: {e}", "danger")

    return redirect(url_for("dashboard"))

@app.route("/student/update", methods=["POST"], strict_slashes=False)
def update_student():
    if "user" not in session:
        return redirect(url_for("login"))

    student_id = request.form.get("id")
    name = request.form.get("name", "").strip()
    age = request.form.get("age")
    branch = request.form.get("branch", "").strip()
    address = request.form.get("address", "").strip()
    email = request.form.get("email", "").strip()

    try:
        con = get_connection()
        cur = con.cursor()
        query = """UPDATE student 
                   SET name = %s, age = %s, branch = %s, address = %s, email = %s 
                   WHERE id = %s"""
        cur.execute(query, (name, age, branch, address, email, student_id))
        con.commit()
        cur.close()
        con.close()
        flash(f"Student ID {student_id} updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating student: {e}", "danger")

    return redirect(url_for("dashboard"))

@app.route("/student/delete/<int:id>", strict_slashes=False)
def delete_student(id):
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM student WHERE id = %s", (id,))
        con.commit()
        cur.close()
        con.close()
        flash(f"Student ID {id} deleted successfully!", "info")
    except Exception as e:
        flash(f"Error deleting record: {e}", "danger")

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)