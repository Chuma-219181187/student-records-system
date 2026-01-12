-- sql/create_tables.sql

CREATE TABLE students (
    student_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    dob DATE NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    CHECK (email LIKE '%@%')
);

CREATE TABLE courses (
    course_id INT IDENTITY(1,1) PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    credits INT NOT NULL CHECK (credits BETWEEN 1 AND 10)
);

CREATE TABLE enrollments (
    enrollment_id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(student_id),
    course_id INT NOT NULL REFERENCES courses(course_id),
    enrollment_date DATE NOT NULL,
    UNIQUE(student_id, course_id)
);

CREATE TABLE grades (
    grade_id INT IDENTITY(1,1) PRIMARY KEY,
    enrollment_id INT UNIQUE NOT NULL REFERENCES enrollments(enrollment_id),
    grade NUMERIC(5,2) CHECK (grade BETWEEN 0 AND 100)
);

CREATE TABLE attendance (
    attendance_id INT IDENTITY(1,1) PRIMARY KEY,
    enrollment_id INT NOT NULL REFERENCES enrollments(enrollment_id),
    attendance_date DATE NOT NULL,
    status VARCHAR(10) CHECK (status IN ('Present','Absent','Late'))
);

CREATE INDEX idx_student_course ON enrollments(student_id, course_id);

