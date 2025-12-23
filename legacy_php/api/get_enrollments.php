$sql = "SELECT e.id AS enrollment_id, p.name, e.status, e.enrollment_date
        FROM enrollments e
        JOIN programs p ON e.program_id = p.id
        WHERE e.beneficiary_id = ?";
