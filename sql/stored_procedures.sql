-- sql/stored_procedures.sql
CREATE OR REPLACE FUNCTION enroll_student(p_student INT, p_course INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO enrollments(student_id,course_id,enrollment_date)
    VALUES (p_student,p_course,CURRENT_DATE)
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;
