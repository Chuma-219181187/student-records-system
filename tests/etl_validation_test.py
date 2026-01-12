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

tests = [
    ("Students loaded", "SELECT COUNT(*) > 0 FROM students"),
    ("Courses loaded", "SELECT COUNT(*) > 0 FROM courses"),
    ("No null emails", "SELECT COUNT(*) = 0 FROM students WHERE email IS NULL"),
]

for name, query in tests:
    cur.execute(query)
    result = cur.fetchone()[0]
    print(f"{name}: {'PASS' if result else 'FAIL'}")

conn.close()
