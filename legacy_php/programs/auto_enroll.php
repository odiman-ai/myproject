<?php
include 'db_config.php';

// Get all beneficiaries
$b_query = $conn->query("SELECT id, dob, location FROM beneficiaries");

while ($b = $b_query->fetch_assoc()) {
    $age = (new DateTime($b['dob']))->diff(new DateTime())->y;

    // Get matching programs
    $p_query = $conn->prepare("SELECT id FROM programs WHERE ? BETWEEN eligibility_age_min AND eligibility_age_max AND location = ?");
    $p_query->bind_param("is", $age, $b['location']);
    $p_query->execute();
    $p_result = $p_query->get_result();

    while ($p = $p_result->fetch_assoc()) {
        // Check if already enrolled
        $check = $conn->prepare("SELECT id FROM enrollments WHERE beneficiary_id = ? AND program_id = ?");
        $check->bind_param("ii", $b['id'], $p['id']);
        $check->execute();
        if ($check->get_result()->num_rows === 0) {
            // Enroll
            $enroll = $conn->prepare("INSERT INTO enrollments (beneficiary_id, program_id) VALUES (?, ?)");
            $enroll->bind_param("ii", $b['id'], $p['id']);
            $enroll->execute();
        }
    }
}
?>