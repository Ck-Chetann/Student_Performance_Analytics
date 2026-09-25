import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Chetan@2007",
    database="student_performance_db"
)

# Fetch data
query = """
SELECT
    students.student_id,
    students.name,
    subjects.subject_name,
    marks.marks,
    attendance.attendance_percentage
FROM students
INNER JOIN marks
    ON students.student_id = marks.student_id
INNER JOIN subjects
    ON marks.subject_id = subjects.subject_id
INNER JOIN attendance
    ON students.student_id = attendance.student_id
    AND subjects.subject_id = attendance.subject_id
"""

df = pd.read_sql(query, db)

print("===== DATA =====")
print(df)

# --------------------------------
# 1. Student-wise Average Marks
# --------------------------------

student_average = df.groupby("name")["marks"].mean()

print("\n===== STUDENT AVERAGE =====")
print(student_average)

plt.figure(figsize=(8, 5))
student_average.plot(kind="bar")

plt.title("Student-wise Average Marks")
plt.xlabel("Student")
plt.ylabel("Average Marks")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("student_average.png")
plt.show()


# --------------------------------
# 2. Subject-wise Average Marks
# --------------------------------

subject_average = df.groupby("subject_name")["marks"].mean()

print("\n===== SUBJECT AVERAGE =====")
print(subject_average)

plt.figure(figsize=(8, 5))
subject_average.plot(kind="bar")

plt.title("Subject-wise Average Marks")
plt.xlabel("Subject")
plt.ylabel("Average Marks")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("subject_average.png")
plt.show()


# --------------------------------
# 3. Attendance vs Marks
# --------------------------------

plt.figure(figsize=(8, 5))

plt.scatter(
    df["attendance_percentage"],
    df["marks"]
)

plt.title("Attendance vs Marks")
plt.xlabel("Attendance Percentage")
plt.ylabel("Marks")

plt.tight_layout()

plt.savefig("attendance_vs_marks.png")
plt.show()


# --------------------------------
# 4. Overall Statistics
# --------------------------------

average_marks = df["marks"].mean()
average_attendance = df["attendance_percentage"].mean()

pass_students = df.groupby("name")["marks"].mean() >= 40
pass_percentage = pass_students.mean() * 100

correlation = df["marks"].corr(
    df["attendance_percentage"]
)

print("\n===== OVERALL ANALYSIS =====")

print("Average Marks:",
      round(average_marks, 2))

print("Average Attendance:",
      round(average_attendance, 2))

print("Pass Percentage:",
      round(pass_percentage, 2), "%")

print("Attendance vs Marks Correlation:",
      round(correlation, 2))


db.close()

print("\nAnalysis completed successfully!")