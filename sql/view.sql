-- SQL Server Views for Student Records System

-- Drop views if they exist (SQL Server syntax)
IF OBJECT_ID('vw_at_risk_students', 'V') IS NOT NULL DROP VIEW vw_at_risk_students;
IF OBJECT_ID('vw_course_performance', 'V') IS NOT NULL DROP VIEW vw_course_performance;
IF OBJECT_ID('vw_attendance_summary', 'V') IS NOT NULL DROP VIEW vw_attendance_summary;
IF OBJECT_ID('vw_course_roster', 'V') IS NOT NULL DROP VIEW vw_course_roster;
IF OBJECT_ID('vw_student_transcript', 'V') IS NOT NULL DROP VIEW vw_student_transcript;
GO

-- View 1: Student Transcript
-- Combines student information with their enrolled courses and corresponding grades
CREATE VIEW vw_student_transcript AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    s.email,
    c.course_id,
    c.course_name,
    c.course_code,
    g.grade
FROM students s
JOIN enrollments e
    ON e.student_id = s.student_id
JOIN courses c
    ON c.course_id = e.course_id
LEFT JOIN grades g
    ON g.enrollment_id = e.enrollment_id;
GO

-- View 2: Course Roster
-- Lists all students enrolled in each course along with their enrollment dates
CREATE VIEW vw_course_roster AS
SELECT
    c.course_id,
    c.course_name,
    c.course_code,
    s.student_id,
    s.first_name,
    s.last_name,
    e.enrollment_date
FROM courses c
JOIN enrollments e
    ON e.course_id = c.course_id
JOIN students s
    ON s.student_id = e.student_id;
GO

-- View 3: Attendance Summary
-- Provides a summary of attendance percentages for each student in their enrolled courses
CREATE VIEW vw_attendance_summary AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    c.course_id,
    c.course_name,
    ROUND(
        (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0)
        / COUNT(a.attendance_id),
        2
    ) AS attendance_percentage
FROM attendance a
JOIN enrollments e
    ON e.enrollment_id = a.enrollment_id
JOIN students s
    ON s.student_id = e.student_id
JOIN courses c
    ON c.course_id = e.course_id
GROUP BY
    s.student_id,
    s.first_name,
    s.last_name,
    c.course_id,
    c.course_name;
GO

-- View 4: Course Performance
-- Summarizes the average grade for each course
CREATE VIEW vw_course_performance AS
SELECT
    c.course_id,
    c.course_name,
    c.course_code,
    ROUND(AVG(CAST(g.grade AS FLOAT)), 2) AS average_grade
FROM courses c
LEFT JOIN enrollments e
    ON e.course_id = c.course_id
LEFT JOIN grades g
    ON g.enrollment_id = e.enrollment_id
GROUP BY
    c.course_id,
    c.course_name,
    c.course_code;
GO

-- View 5: At-Risk Students
-- Identifies students who are at risk due to low attendance (below 75%)
CREATE VIEW vw_at_risk_students AS
SELECT
    student_id,
    first_name,
    last_name,
    course_name,
    attendance_percentage
FROM vw_attendance_summary
WHERE attendance_percentage < 75;
GO

