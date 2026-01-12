from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
)
cur = conn.cursor()

def generate_transcript(student_id):
    cur.execute("""
        SELECT first_name, last_name, gpa
        FROM students
        WHERE student_id = %s
    """, (student_id,))
    s = cur.fetchone()

    cur.execute("""
        SELECT c.course_name, g.grade
        FROM grades g
        JOIN enrollments e ON e.enrollment_id = g.enrollment_id
        JOIN courses c ON c.course_id = e.course_id
        WHERE e.student_id = %s
    """, (student_id,))
    rows = cur.fetchall()

    pdf = canvas.Canvas(f"transcript_{student_id}.pdf", pagesize=A4)
    pdf.drawString(50, 800, f"Student Transcript — {s[0]} {s[1]}")
    pdf.drawString(50, 780, f"GPA: {round(s[2],2) if s[2] else 'N/A'}")

    y = 740
    for course, grade in rows:
        pdf.drawString(50, y, f"{course} — {grade}")
        y -= 20

    pdf.save()
    print("Transcript generated.")

if __name__ == "__main__":
    sid = int(input("Enter Student ID: "))
    generate_transcript(sid)
