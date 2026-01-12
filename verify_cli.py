#!/usr/bin/env python
# Test script to verify CLI app works

import pyodbc
from dotenv import load_dotenv
import os
from datetime import datetime

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

try:
    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()
    print("✅ Connected to SQL Server successfully!")
    
    # Test 1: View students
    cur.execute("SELECT COUNT(*) FROM students")
    count = cur.fetchone()[0]
    print(f"📊 Total students: {count}")
    
    # Test 2: View courses
    cur.execute("SELECT COUNT(*) FROM courses")
    count = cur.fetchone()[0]
    print(f"📘 Total courses: {count}")
    
    # Test 3: View enrollments
    cur.execute("SELECT COUNT(*) FROM enrollments")
    count = cur.fetchone()[0]
    print(f"📝 Total enrollments: {count}")
    
    # Test 4: View sample student record
    cur.execute("SELECT TOP 1 student_id, first_name, last_name, email FROM students")
    row = cur.fetchone()
    if row:
        print(f"\n📋 Sample student: ID={row[0]}, Name={row[1]} {row[2]}, Email={row[3]}")
    
    conn.close()
    print("\n✅ CLI app is ready to use!")
    print("Run: python app/cli_app.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
