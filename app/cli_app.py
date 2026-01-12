# app/cli_app.py
import pyodbc
from dotenv import load_dotenv
import os
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ------------------ ENV + DB ------------------
load_dotenv()

conn_str = f"""
Driver={{ODBC Driver 17 for SQL Server}};
Server=tcp:{os.getenv('DB_HOST')},1433;
Database={os.getenv('DB_NAME')};
Uid={os.getenv('DB_USER')};
Pwd={os.getenv('DB_PASS')};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
"""

conn = pyodbc.connect(conn_str)
cur = conn.cursor()

# ------------------ VALIDATION ------------------
def validate_email(email):
    return "@" in email and "." in email

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# ------------------ CRUD OPERATIONS ------------------
def add_student():
    print("\n➕ Add Student")
    first = input("First name: ")
    last = input("Last name: ")
    email = input("Email: ")
    dob = input("DOB (YYYY-MM-DD): ")

    if not validate_email(email):
        print("❌ Invalid email.")
        return

    if not validate_date(dob):
        print("❌ Invalid date format.")
        return

    try:
        cur.execute("""
            INSERT INTO students(first_name, last_name, email, dob)
            VALUES (?, ?, ?, ?)
        """, (first, last, email, dob))
        conn.commit()
        print("✅ Student added successfully.")
    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)


def enroll_student():
    print("\n📘 Enroll Student in Course")
    student_id = input("Student ID: ")
    course_id = input("Course ID: ")

    try:
        cur.execute("""
            INSERT INTO enrollments(student_id, course_id, enrollment_date)
            VALUES (?, ?, CAST(GETDATE() AS DATE))
        """, (student_id, course_id))
        conn.commit()
        print("✅ Enrollment successful.")
    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)


def record_grade():
    print("\n📝 Record Grade")
    enrollment_id = input("Enrollment ID: ")
    grade = float(input("Grade (0–100): "))

    if grade < 0 or grade > 100:
        print("❌ Grade must be between 0 and 100.")
        return

    try:
        cur.execute("""
            MERGE INTO grades AS target
            USING (SELECT ? AS enrollment_id, ? AS grade) AS source
            ON target.enrollment_id = source.enrollment_id
            WHEN MATCHED THEN UPDATE SET grade = source.grade
            WHEN NOT MATCHED THEN INSERT (enrollment_id, grade) VALUES (source.enrollment_id, source.grade);
        """, (enrollment_id, grade))
        conn.commit()
        print("✅ Grade recorded.")
    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)


def mark_attendance():
    print("\n📅 Mark Attendance")
    enrollment_id = input("Enrollment ID: ")
    date = input("Date (YYYY-MM-DD): ")
    status = input("Status (Present / Absent / Late): ")

    if not validate_date(date):
        print("❌ Invalid date.")
        return

    if status not in ["Present", "Absent", "Late"]:
        print("❌ Invalid status.")
        return

    try:
        cur.execute("""
            INSERT INTO attendance(enrollment_id, attendance_date, status)
            VALUES (?, ?, ?)
        """, (enrollment_id, date, status))
        conn.commit()
        print("✅ Attendance recorded.")
    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)

# ------------------ REPORTS ------------------
def generate_csv_report():
    print("\n📊 Generate CSV Report")

    cur.execute("""
        SELECT s.student_id, s.first_name, s.last_name,
               c.course_name, g.grade
        FROM students s
        JOIN enrollments e ON e.student_id = s.student_id
        JOIN courses c ON c.course_id = e.course_id
        LEFT JOIN grades g ON g.enrollment_id = e.enrollment_id
    """)

    rows = cur.fetchall()

    with open("student_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "First Name", "Last Name", "Course", "Grade"])
        writer.writerows(rows)

    print("✅ CSV report generated: student_report.csv")


def generate_pdf_transcript():
    print("\n📄 Generate PDF Transcript")
    student_id = input("Student ID: ")

    cur.execute("""
        SELECT first_name, last_name
        FROM students WHERE student_id = ?
    """, (student_id,))
    student = cur.fetchone()

    if not student:
        print("❌ Student not found.")
        return

    cur.execute("""
        SELECT c.course_name, g.grade
        FROM enrollments e
        JOIN courses c ON c.course_id = e.course_id
        LEFT JOIN grades g ON g.enrollment_id = e.enrollment_id
        WHERE e.student_id = ?
    """, (student_id,))
    records = cur.fetchall()

    file_name = f"transcript_{student_id}.pdf"
    pdf = canvas.Canvas(file_name, pagesize=A4)

    pdf.drawString(50, 800, f"Transcript: {student[0]} {student[1]}")

    y = 760
    for course, grade in records:
        pdf.drawString(50, y, f"{course}: {grade}")
        y -= 20

    pdf.save()
    print(f"✅ PDF transcript generated: {file_name}")

# ------------------ MENU ------------------
def menu():
    while True:
        print("""
=============================
STUDENT RECORDS CLI SYSTEM
=============================
1. Add Student
2. Enroll Student
3. Record Grade
4. Mark Attendance
5. Generate CSV Report
6. Generate PDF Transcript
0. Exit
""")
        choice = input("Select option: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            enroll_student()
        elif choice == "3":
            record_grade()
        elif choice == "4":
            mark_attendance()
        elif choice == "5":
            generate_csv_report()
        elif choice == "6":
            generate_pdf_transcript()
        elif choice == "0":
            print("👋 Exiting system.")
            break
        else:
            print("❌ Invalid choice.")

    conn.close()

# ------------------ RUN ------------------
if __name__ == "__main__":
    menu()
