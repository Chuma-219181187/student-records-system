-- Top 10 students by GPA
SELECT student_id, gpa
FROM students
ORDER BY gpa DESC
LIMIT 10;

-- Course average grade
SELECT c.course_name, AVG(g.grade) AS avg_grade
FROM grades g
JOIN enrollments e ON e.enrollment_id = g.enrollment_id
JOIN courses c ON c.course_id = e.course_id
GROUP BY c.course_name;

-- Students at attendance risk (<75%)
SELECT s.student_id, s.first_name, s.last_name,
       ROUND(
        (SUM(CASE WHEN a.status='Present' THEN 1 END) * 100.0) / COUNT(*),2
       ) AS attendance_rate
FROM attendance a
JOIN enrollments e ON e.enrollment_id = a.enrollment_id
JOIN students s ON s.student_id = e.student_id
GROUP BY s.student_id, s.first_name, s.last_name
HAVING (
    (SUM(CASE WHEN a.status='Present' THEN 1 END) * 100.0) / COUNT(*)
) < 75;
