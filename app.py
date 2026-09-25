from flask import Flask, render_template, request, redirect
import mysql.connector
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ==============================
# MACHINE LEARNING MODEL
# ==============================

ml_data = pd.read_csv("ml/training_data.csv")

X = ml_data[["attendance", "average_marks"]]
y = ml_data["result"]

model = DecisionTreeClassifier(
    random_state=42,
    max_depth=4
)

model.fit(X, y)

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# VIEW + SEARCH STUDENTS
# ==========================================

@app.route("/students")
def students():

    search = request.args.get("search", "")

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if search:

        query = """
        SELECT * FROM students
        WHERE name LIKE %s
        OR email LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(query, (value, value))

    else:

        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "students.html",
        students=students,
        search=search
    )


# ==========================================
# ADD STUDENT
# ==========================================

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        year = request.form["year"]

        db = get_db_connection()

        cursor = db.cursor()

        query = """
        INSERT INTO students
        (name, email, department, year)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            name,
            email,
            department,
            year
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()
        db.close()

        return redirect("/students")

    return render_template("add_student.html")


# ==========================================
# EDIT STUDENT
# ==========================================

@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        year = request.form["year"]

        query = """
        UPDATE students
        SET name = %s,
            email = %s,
            department = %s,
            year = %s
        WHERE student_id = %s
        """

        values = (
            name,
            email,
            department,
            year,
            student_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()
        db.close()

        return redirect("/students")

    cursor.execute(
        "SELECT * FROM students WHERE student_id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route("/delete-student/<int:student_id>")
def delete_student(student_id):

    db = get_db_connection()

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE student_id = %s",
        (student_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/students")

# ==========================================
# VIEW SUBJECTS
# ==========================================

@app.route("/subjects")
def subjects():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subjects")

    subjects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


# ==========================================
# ADD SUBJECT
# ==========================================

@app.route("/add-subject", methods=["GET", "POST"])
def add_subject():

    if request.method == "POST":

        subject_name = request.form["subject_name"]
        credits = request.form["credits"]

        db = get_db_connection()

        cursor = db.cursor()

        query = """
        INSERT INTO subjects
        (subject_name, credits)
        VALUES (%s, %s)
        """

        cursor.execute(
            query,
            (subject_name, credits)
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/subjects")

    return render_template("add_subject.html")


# ==========================================
# EDIT SUBJECT
# ==========================================

@app.route(
    "/edit-subject/<int:subject_id>",
    methods=["GET", "POST"]
)
def edit_subject(subject_id):

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        subject_name = request.form["subject_name"]
        credits = request.form["credits"]

        query = """
        UPDATE subjects
        SET subject_name = %s,
            credits = %s
        WHERE subject_id = %s
        """

        cursor.execute(
            query,
            (
                subject_name,
                credits,
                subject_id
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/subjects")

    cursor.execute(
        "SELECT * FROM subjects WHERE subject_id = %s",
        (subject_id,)
    )

    subject = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "edit_subject.html",
        subject=subject
    )


# ==========================================
# DELETE SUBJECT
# ==========================================

@app.route("/delete-subject/<int:subject_id>")
def delete_subject(subject_id):

    db = get_db_connection()

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM subjects WHERE subject_id = %s",
        (subject_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/subjects")

# ==========================================
# VIEW MARKS
# ==========================================

@app.route("/marks")
def marks():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        marks.mark_id,
        marks.student_id,
        marks.subject_id,
        students.name AS student_name,
        subjects.subject_name,
        marks.marks
    FROM marks

    INNER JOIN students
        ON marks.student_id = students.student_id

    INNER JOIN subjects
        ON marks.subject_id = subjects.subject_id

    ORDER BY marks.mark_id
    """

    cursor.execute(query)

    marks_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "marks.html",
        marks=marks_data
    )


# ==========================================
# ADD MARKS
# ==========================================

@app.route("/add-marks", methods=["GET", "POST"])
def add_marks():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        marks_value = request.form["marks"]

        cursor.execute(
            """
            INSERT INTO marks
            (student_id, subject_id, marks)
            VALUES (%s, %s, %s)
            """,
            (
                student_id,
                subject_id,
                marks_value
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/marks")

    cursor.execute(
        "SELECT * FROM students ORDER BY name"
    )

    students = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM subjects ORDER BY subject_name"
    )

    subjects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "add_marks.html",
        students=students,
        subjects=subjects
    )


# ==========================================
# EDIT MARKS
# ==========================================

@app.route(
    "/edit-marks/<int:mark_id>",
    methods=["GET", "POST"]
)
def edit_marks(mark_id):

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        marks_value = request.form["marks"]

        cursor.execute(
            """
            UPDATE marks

            SET student_id = %s,
                subject_id = %s,
                marks = %s

            WHERE mark_id = %s
            """,
            (
                student_id,
                subject_id,
                marks_value,
                mark_id
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/marks")

    cursor.execute(
        "SELECT * FROM marks WHERE mark_id = %s",
        (mark_id,)
    )

    mark = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM students ORDER BY name"
    )

    students = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM subjects ORDER BY subject_name"
    )

    subjects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "edit_marks.html",
        mark=mark,
        students=students,
        subjects=subjects
    )


# ==========================================
# DELETE MARKS
# ==========================================

@app.route("/delete-marks/<int:mark_id>")
def delete_marks(mark_id):

    db = get_db_connection()

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM marks WHERE mark_id = %s",
        (mark_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/marks")

# ==========================================
# VIEW ATTENDANCE
# ==========================================

@app.route("/attendance")
def attendance():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        attendance.attendance_id,
        attendance.student_id,
        attendance.subject_id,
        students.name AS student_name,
        subjects.subject_name,
        attendance.attendance_percentage
    FROM attendance

    INNER JOIN students
        ON attendance.student_id = students.student_id

    INNER JOIN subjects
        ON attendance.subject_id = subjects.subject_id

    ORDER BY attendance.attendance_id
    """

    cursor.execute(query)

    attendance_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "attendance.html",
        attendance_data=attendance_data
    )


# ==========================================
# ADD ATTENDANCE
# ==========================================

@app.route("/add-attendance", methods=["GET", "POST"])
def add_attendance():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        attendance_percentage = request.form[
            "attendance_percentage"
        ]

        # Server-side validation
        attendance_value = float(attendance_percentage)

        if attendance_value < 0 or attendance_value > 100:

            cursor.close()
            db.close()

            return "Attendance must be between 0 and 100."

        cursor.execute(
            """
            INSERT INTO attendance
            (student_id, subject_id, attendance_percentage)
            VALUES (%s, %s, %s)
            """,
            (
                student_id,
                subject_id,
                attendance_value
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/attendance")

    cursor.execute(
        "SELECT * FROM students ORDER BY name"
    )

    students = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM subjects ORDER BY subject_name"
    )

    subjects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "add_attendance.html",
        students=students,
        subjects=subjects
    )


# ==========================================
# EDIT ATTENDANCE
# ==========================================

@app.route(
    "/edit-attendance/<int:attendance_id>",
    methods=["GET", "POST"]
)
def edit_attendance(attendance_id):

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        attendance_percentage = request.form[
            "attendance_percentage"
        ]

        attendance_value = float(attendance_percentage)

        if attendance_value < 0 or attendance_value > 100:

            cursor.close()
            db.close()

            return "Attendance must be between 0 and 100."

        cursor.execute(
            """
            UPDATE attendance

            SET student_id = %s,
                subject_id = %s,
                attendance_percentage = %s

            WHERE attendance_id = %s
            """,
            (
                student_id,
                subject_id,
                attendance_value,
                attendance_id
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect("/attendance")

    cursor.execute(
        """
        SELECT *
        FROM attendance
        WHERE attendance_id = %s
        """,
        (attendance_id,)
    )

    attendance = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM students ORDER BY name"
    )

    students = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM subjects ORDER BY subject_name"
    )

    subjects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "edit_attendance.html",
        attendance=attendance,
        students=students,
        subjects=subjects
    )


# ==========================================
# DELETE ATTENDANCE
# ==========================================

@app.route("/delete-attendance/<int:attendance_id>")
def delete_attendance(attendance_id):

    db = get_db_connection()

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM attendance
        WHERE attendance_id = %s
        """,
        (attendance_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/attendance")

# ==========================================
# STUDENT PERFORMANCE
# ==========================================

@app.route("/performance")
def performance():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        students.student_id,
        students.name,

        COALESCE(
            (
                SELECT AVG(marks.marks)
                FROM marks
                WHERE marks.student_id = students.student_id
            ),
            0
        ) AS average_marks,

        COALESCE(
            (
                SELECT AVG(attendance.attendance_percentage)
                FROM attendance
                WHERE attendance.student_id = students.student_id
            ),
            0
        ) AS average_attendance

    FROM students

    ORDER BY students.name
    """

    cursor.execute(query)

    performance_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "performance.html",
        performance=performance_data
    )

@app.route("/dashboard")
def dashboard():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Total Students
    cursor.execute(
        "SELECT COUNT(*) AS total_students FROM students"
    )
    total_students = cursor.fetchone()["total_students"]

    # Total Subjects
    cursor.execute(
        "SELECT COUNT(*) AS total_subjects FROM subjects"
    )
    total_subjects = cursor.fetchone()["total_subjects"]

    # Average Marks
    cursor.execute(
        "SELECT AVG(marks) AS average_marks FROM marks"
    )

    result = cursor.fetchone()
    average_marks = result["average_marks"] or 0

    # Average Attendance
    cursor.execute(
        "SELECT AVG(attendance_percentage) AS average_attendance FROM attendance"
    )

    result = cursor.fetchone()
    average_attendance = result["average_attendance"] or 0

    # Pass Percentage
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN average_marks >= 40 THEN 1
                    ELSE 0
                END
            ) AS passed
        FROM (
            SELECT
                student_id,
                AVG(marks) AS average_marks
            FROM marks
            GROUP BY student_id
        ) AS performance
    """)

    result = cursor.fetchone()

    if result["total"] > 0:
        pass_percentage = (
            result["passed"] / result["total"]
        ) * 100
    else:
        pass_percentage = 0

    # Student-wise Average Marks
    cursor.execute("""
        SELECT
            students.name,
            AVG(marks.marks) AS average_marks
        FROM students
        INNER JOIN marks
            ON students.student_id = marks.student_id
        GROUP BY students.student_id, students.name
        ORDER BY average_marks DESC
    """)

    student_performance = cursor.fetchall()

    # Subject-wise Average Marks
    cursor.execute("""
        SELECT
            subjects.subject_name,
            AVG(marks.marks) AS average_marks
        FROM subjects
        INNER JOIN marks
            ON subjects.subject_id = marks.subject_id
        GROUP BY subjects.subject_id, subjects.subject_name
        ORDER BY average_marks DESC
    """)

    subject_performance = cursor.fetchall()

    # Data for Charts
    student_names = [
        student["name"]
        for student in student_performance
    ]

    student_marks = [
        float(student["average_marks"])
        for student in student_performance
    ]

    subject_names = [
        subject["subject_name"]
        for subject in subject_performance
    ]

    subject_marks = [
        float(subject["average_marks"])
        for subject in subject_performance
    ]

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_subjects=total_subjects,
        average_marks=round(average_marks, 2),
        average_attendance=round(average_attendance, 2),
        pass_percentage=round(pass_percentage, 2),
        student_performance=student_performance,
        subject_performance=subject_performance,
        student_names=student_names,
        student_marks=student_marks,
        subject_names=subject_names,
        subject_marks=subject_marks
    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    result = None

    if request.method == "POST":

        attendance = float(request.form["attendance"])
        average_marks = float(request.form["average_marks"])

        # Validation
        if attendance < 0 or attendance > 100:
            result = "Invalid Attendance"

        elif average_marks < 0 or average_marks > 100:
            result = "Invalid Marks"

        else:

            new_student = pd.DataFrame({
                "attendance": [attendance],
                "average_marks": [average_marks]
            })

            prediction_value = model.predict(new_student)

            if prediction_value[0] == 1:
                result = "PASS"
            else:
                result = "FAIL"

    return render_template(
        "prediction.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)