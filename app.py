"""
Student Management System — Flask Application
Tech Stack: Python (Flask) + MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = "sms_secret_key_2024"

# ─────────────────────────────────────────
#  DB CONNECTION  — update credentials here
# ─────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "9835",   # ← change this
    "database": "student_management",
    "autocommit": True,
}

def get_db():
    """Return a fresh MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"DB Connection Error: {e}")
        return None


def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    """Helper: run a query and return results."""
    conn = get_db()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        if commit:
            conn.commit()
            return cur.lastrowid
    except Error as e:
        print(f"Query Error: {e}")
        return None
    finally:
        conn.close()


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────
@app.route("/")
def dashboard():
    stats = {
        "students":    (query("SELECT COUNT(*) AS c FROM students WHERE status='Active'", fetchone=True) or {}).get("c", 0),
        "courses":     (query("SELECT COUNT(*) AS c FROM courses",                        fetchone=True) or {}).get("c", 0),
        "departments": (query("SELECT COUNT(*) AS c FROM departments",                    fetchone=True) or {}).get("c", 0),
        "fees_due":    (query("SELECT COUNT(*) AS c FROM fees WHERE status='Pending'",    fetchone=True) or {}).get("c", 0),
    }
    recent = query(
        "SELECT s.roll_number, s.first_name, s.last_name, d.dept_name, s.year_of_study, s.status "
        "FROM students s LEFT JOIN departments d ON s.dept_id=d.dept_id "
        "ORDER BY s.created_at DESC LIMIT 5",
        fetchall=True
    ) or []
    return render_template("dashboard.html", stats=stats, recent=recent)


# ─────────────────────────────────────────
#  STUDENTS — CRUD
# ─────────────────────────────────────────
@app.route("/students")
def students():
    rows = query(
        "SELECT s.*, d.dept_name FROM students s "
        "LEFT JOIN departments d ON s.dept_id=d.dept_id ORDER BY s.student_id",
        fetchall=True
    ) or []
    return render_template("students.html", students=rows)


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    depts = query("SELECT * FROM departments", fetchall=True) or []
    if request.method == "POST":
        f = request.form
        query(
            "INSERT INTO students (roll_number,first_name,last_name,email,phone,dob,gender,address,dept_id,section,year_of_study) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (f["roll_number"], f["first_name"], f["last_name"], f["email"],
             f.get("phone"), f.get("dob") or None, f.get("gender"),
             f.get("address"), f.get("dept_id") or None,
             f.get("section"), f.get("year_of_study", 1)),
            commit=True
        )
        flash("Student registered successfully!", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", depts=depts, student=None)


@app.route("/students/edit/<int:sid>", methods=["GET", "POST"])
def edit_student(sid):
    depts   = query("SELECT * FROM departments", fetchall=True) or []
    student = query("SELECT * FROM students WHERE student_id=%s", (sid,), fetchone=True)
    if not student:
        flash("Student not found", "danger")
        return redirect(url_for("students"))
    if request.method == "POST":
        f = request.form
        query(
            "UPDATE students SET roll_number=%s,first_name=%s,last_name=%s,email=%s,phone=%s,"
            "dob=%s,gender=%s,address=%s,dept_id=%s,section=%s,year_of_study=%s,status=%s "
            "WHERE student_id=%s",
            (f["roll_number"], f["first_name"], f["last_name"], f["email"],
             f.get("phone"), f.get("dob") or None, f.get("gender"),
             f.get("address"), f.get("dept_id") or None,
             f.get("section"), f.get("year_of_study", 1), f.get("status","Active"), sid),
            commit=True
        )
        flash("Student updated successfully!", "success")
        return redirect(url_for("students"))
    return render_template("student_form.html", depts=depts, student=student)


@app.route("/students/delete/<int:sid>")
def delete_student(sid):
    query("DELETE FROM students WHERE student_id=%s", (sid,), commit=True)
    flash("Student deleted.", "warning")
    return redirect(url_for("students"))


@app.route("/students/view/<int:sid>")
def view_student(sid):
    student = query(
        "SELECT s.*, d.dept_name FROM students s "
        "LEFT JOIN departments d ON s.dept_id=d.dept_id WHERE s.student_id=%s",
        (sid,), fetchone=True
    )
    if not student:
        flash("Student not found", "danger")
        return redirect(url_for("students"))
    enrolls = query(
        "SELECT c.course_name, c.course_code, e.semester FROM enrollments e "
        "JOIN courses c ON e.course_id=c.course_id WHERE e.student_id=%s",
        (sid,), fetchall=True
    ) or []
    marks = query(
        "SELECT c.course_name, m.internal_marks, m.external_marks, m.total_marks, m.grade, m.semester "
        "FROM marks m JOIN courses c ON m.course_id=c.course_id WHERE m.student_id=%s",
        (sid,), fetchall=True
    ) or []
    fees = query("SELECT * FROM fees WHERE student_id=%s ORDER BY due_date", (sid,), fetchall=True) or []
    att_summary = query(
        "SELECT c.course_name, "
        "SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present, "
        "COUNT(*) AS total "
        "FROM attendance a JOIN courses c ON a.course_id=c.course_id "
        "WHERE a.student_id=%s GROUP BY a.course_id",
        (sid,), fetchall=True
    ) or []
    return render_template("student_view.html", student=student,
                           enrolls=enrolls, marks=marks, fees=fees, att_summary=att_summary)


# ─────────────────────────────────────────
#  COURSES
# ─────────────────────────────────────────
@app.route("/courses")
def courses():
    rows = query(
        "SELECT c.*, d.dept_name, "
        "(SELECT COUNT(*) FROM enrollments e WHERE e.course_id=c.course_id) AS enrolled "
        "FROM courses c LEFT JOIN departments d ON c.dept_id=d.dept_id",
        fetchall=True
    ) or []
    return render_template("courses.html", courses=rows)


@app.route("/courses/add", methods=["GET","POST"])
def add_course():
    depts = query("SELECT * FROM departments", fetchall=True) or []
    if request.method == "POST":
        f = request.form
        query(
            "INSERT INTO courses (course_name,course_code,credits,dept_id) VALUES (%s,%s,%s,%s)",
            (f["course_name"], f["course_code"], f.get("credits",3), f.get("dept_id") or None),
            commit=True
        )
        flash("Course added!", "success")
        return redirect(url_for("courses"))
    return render_template("course_form.html", depts=depts, course=None)


@app.route("/courses/delete/<int:cid>")
def delete_course(cid):
    query("DELETE FROM courses WHERE course_id=%s", (cid,), commit=True)
    flash("Course deleted.", "warning")
    return redirect(url_for("courses"))


# ─────────────────────────────────────────
#  ENROLLMENTS
# ─────────────────────────────────────────
@app.route("/enrollments")
def enrollments():
    rows = query(
        "SELECT e.enrollment_id, s.first_name, s.last_name, s.roll_number, "
        "c.course_name, c.course_code, e.semester, e.enrolled_on "
        "FROM enrollments e "
        "JOIN students s ON e.student_id=s.student_id "
        "JOIN courses c  ON e.course_id=c.course_id "
        "ORDER BY e.enrollment_id DESC",
        fetchall=True
    ) or []
    students_list = query("SELECT student_id,roll_number,first_name,last_name FROM students WHERE status='Active'", fetchall=True) or []
    courses_list  = query("SELECT course_id,course_name,course_code FROM courses", fetchall=True) or []
    return render_template("enrollments.html", enrollments=rows,
                           students_list=students_list, courses_list=courses_list)


@app.route("/enrollments/add", methods=["POST"])
def add_enrollment():
    f = request.form
    try:
        query(
            "INSERT INTO enrollments (student_id,course_id,semester) VALUES (%s,%s,%s)",
            (f["student_id"], f["course_id"], f["semester"]),
            commit=True
        )
        flash("Enrollment added!", "success")
    except Exception:
        flash("Enrollment already exists for this student/course/semester.", "danger")
    return redirect(url_for("enrollments"))


@app.route("/enrollments/delete/<int:eid>")
def delete_enrollment(eid):
    query("DELETE FROM enrollments WHERE enrollment_id=%s", (eid,), commit=True)
    flash("Enrollment removed.", "warning")
    return redirect(url_for("enrollments"))


# ─────────────────────────────────────────
#  ATTENDANCE
# ─────────────────────────────────────────
@app.route("/attendance")
def attendance():
    records = query(
        "SELECT a.attendance_id, s.first_name, s.last_name, s.roll_number, "
        "c.course_name, a.att_date, a.status "
        "FROM attendance a "
        "JOIN students s ON a.student_id=s.student_id "
        "JOIN courses c  ON a.course_id=c.course_id "
        "ORDER BY a.att_date DESC LIMIT 100",
        fetchall=True
    ) or []
    students_list = query("SELECT student_id,roll_number,first_name,last_name FROM students WHERE status='Active'", fetchall=True) or []
    courses_list  = query("SELECT course_id,course_name,course_code FROM courses", fetchall=True) or []
    # Summary per student
    summary = query(
        "SELECT s.roll_number, CONCAT(s.first_name,' ',s.last_name) AS name, "
        "COUNT(*) AS total, "
        "SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present "
        "FROM attendance a JOIN students s ON a.student_id=s.student_id "
        "GROUP BY a.student_id",
        fetchall=True
    ) or []
    return render_template("attendance.html", records=records,
                           students_list=students_list, courses_list=courses_list,
                           summary=summary)


@app.route("/attendance/add", methods=["POST"])
def add_attendance():
    f = request.form
    try:
        query(
            "INSERT INTO attendance (student_id,course_id,att_date,status) VALUES (%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE status=%s",
            (f["student_id"], f["course_id"], f["att_date"], f["status"], f["status"]),
            commit=True
        )
        flash("Attendance recorded!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("attendance"))


# ─────────────────────────────────────────
#  MARKS / GRADES
# ─────────────────────────────────────────
@app.route("/marks")
def marks():
    rows = query(
        "SELECT m.mark_id, s.roll_number, CONCAT(s.first_name,' ',s.last_name) AS name, "
        "c.course_name, m.semester, m.internal_marks, m.external_marks, m.total_marks, m.grade "
        "FROM marks m "
        "JOIN students s ON m.student_id=s.student_id "
        "JOIN courses c  ON m.course_id=c.course_id "
        "ORDER BY m.mark_id DESC",
        fetchall=True
    ) or []
    students_list = query("SELECT student_id,roll_number,first_name,last_name FROM students WHERE status='Active'", fetchall=True) or []
    courses_list  = query("SELECT course_id,course_name,course_code FROM courses", fetchall=True) or []
    return render_template("marks.html", marks=rows,
                           students_list=students_list, courses_list=courses_list)


@app.route("/marks/add", methods=["POST"])
def add_marks():
    f  = request.form
    im = float(f.get("internal_marks", 0))
    em = float(f.get("external_marks", 0))
    total = im + em
    if   total >= 90: grade = "A+"
    elif total >= 80: grade = "A"
    elif total >= 70: grade = "B+"
    elif total >= 60: grade = "B"
    elif total >= 50: grade = "C"
    else:             grade = "F"
    query(
        "INSERT INTO marks (student_id,course_id,semester,internal_marks,external_marks,grade) "
        "VALUES (%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE internal_marks=%s,external_marks=%s,grade=%s",
        (f["student_id"], f["course_id"], f["semester"], im, em, grade, im, em, grade),
        commit=True
    )
    flash("Marks saved!", "success")
    return redirect(url_for("marks"))


# ─────────────────────────────────────────
#  FEES
# ─────────────────────────────────────────
@app.route("/fees")
def fees():
    rows = query(
        "SELECT f.*, CONCAT(s.first_name,' ',s.last_name) AS name, s.roll_number "
        "FROM fees f JOIN students s ON f.student_id=s.student_id ORDER BY f.due_date",
        fetchall=True
    ) or []
    students_list = query("SELECT student_id,roll_number,first_name,last_name FROM students WHERE status='Active'", fetchall=True) or []
    totals = query(
        "SELECT status, SUM(amount) AS total FROM fees GROUP BY status",
        fetchall=True
    ) or []
    return render_template("fees.html", fees=rows,
                           students_list=students_list, totals=totals)


@app.route("/fees/add", methods=["POST"])
def add_fee():
    f = request.form
    query(
        "INSERT INTO fees (student_id,fee_type,amount,due_date,status) VALUES (%s,%s,%s,%s,%s)",
        (f["student_id"], f["fee_type"], f["amount"], f["due_date"], f.get("status","Pending")),
        commit=True
    )
    flash("Fee record added!", "success")
    return redirect(url_for("fees"))


@app.route("/fees/pay/<int:fid>")
def pay_fee(fid):
    query(
        "UPDATE fees SET status='Paid', paid_date=%s WHERE fee_id=%s",
        (date.today(), fid), commit=True
    )
    flash("Fee marked as Paid!", "success")
    return redirect(url_for("fees"))


@app.route("/fees/delete/<int:fid>")
def delete_fee(fid):
    query("DELETE FROM fees WHERE fee_id=%s", (fid,), commit=True)
    flash("Fee record deleted.", "warning")
    return redirect(url_for("fees"))


# ─────────────────────────────────────────
#  API — for charts
# ─────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    dept_dist = query(
        "SELECT d.dept_name, COUNT(s.student_id) AS count "
        "FROM departments d LEFT JOIN students s ON d.dept_id=s.dept_id "
        "GROUP BY d.dept_id",
        fetchall=True
    ) or []
    grade_dist = query(
        "SELECT grade, COUNT(*) AS count FROM marks GROUP BY grade",
        fetchall=True
    ) or []
    fee_dist = query(
        "SELECT status, COUNT(*) AS count FROM fees GROUP BY status",
        fetchall=True
    ) or []
    return jsonify(dept=dept_dist, grades=grade_dist, fees=fee_dist)


import webbrowser
from threading import Timer


def open_browser():
    """Open the browser after a short delay to ensure server is ready."""
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000")).start()


if __name__ == "__main__":
    open_browser()
    app.run(debug=True, port=5000)
