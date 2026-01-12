# etl/etl_pipeline.py
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root
project_root = os.path.dirname(script_dir)
# Data directory path
data_dir = os.path.join(project_root, "data")

# SQL Server connection using Windows Authentication
conn = pyodbc.connect(
    f'Driver={os.getenv("DB_DRIVER")};'
    f'Server={os.getenv("DB_HOST")};'
    f'Database={os.getenv("DB_NAME")};'
    f'Trusted_Connection=yes;'
)

cur = conn.cursor()

def load_students():
    df = pd.read_csv(os.path.join(data_dir, "students.csv"))
    loaded = 0
    for _, r in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO students(first_name,last_name,email,dob)
                VALUES (?,?,?,?)
            """, (r.first_name,r.last_name,r.email,r.dob))
            loaded += 1
        except pyodbc.IntegrityError:
            pass  # Skip duplicates
    conn.commit()
    print(f"Loaded {loaded} students.")

def load_courses():
    df = pd.read_csv(os.path.join(data_dir, "courses.csv"))
    for _, r in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO courses(course_name,course_code,credits)
                VALUES (?,?,?)
            """, (r.course_name,r.course_code,r.credits))
        except pyodbc.IntegrityError:
            pass  # Skip duplicates
    conn.commit()
    print(f"Loaded {len(df)} courses.")

load_students()
load_courses()
print("ETL Pipeline completed successfully!")
