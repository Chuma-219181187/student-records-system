# etl/generate_sample_data.py
import pandas as pd
from faker import Faker
import random
import os

fake = Faker()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root
project_root = os.path.dirname(script_dir)
# Data directory path
data_dir = os.path.join(project_root, "data")

students = []
for _ in range(300):
    students.append([
        fake.first_name(),
        fake.last_name(),
        fake.email(),
        fake.date_of_birth(minimum_age=18, maximum_age=30)
    ])

courses = [
    ("Database Systems","DB101",4),
    ("Python Programming","PY201",5),
    ("Data Structures","CS301",4),
]

pd.DataFrame(students, columns=[
    "first_name","last_name","email","dob"
]).to_csv(os.path.join(data_dir, "students.csv"), index=False)

pd.DataFrame(courses, columns=[
    "course_name","course_code","credits"
]).to_csv(os.path.join(data_dir, "courses.csv"), index=False)
