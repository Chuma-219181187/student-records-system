-- No NULL emails
SELECT COUNT(*) AS null_emails
FROM students
WHERE email IS NULL;

-- Validate email format
SELECT COUNT(*) AS invalid_emails
FROM students
WHERE email NOT LIKE '%@%';

-- Duplicate email check
SELECT email, COUNT(*)
FROM students
GROUP BY email
HAVING COUNT(*) > 1;

-- Grade range validation
SELECT COUNT(*) AS invalid_grades
FROM grades
WHERE grade NOT BETWEEN 0 AND 100;

-- Orphan enrollment FK check
SELECT COUNT(*) AS broken_enrollments
FROM enrollments e
LEFT JOIN students s ON s.student_id = e.student_id
WHERE s.student_id IS NULL;
