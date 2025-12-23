<?php
include 'db_config.php';

$beneficiary_id = $_GET['id'] ?? null;

if (!$beneficiary_id) {
    echo json_encode(["error" => "Missing beneficiary ID"]);
    exit;
}

// Fetch beneficiary details
$b_query = $conn->prepare("SELECT name, dob, location FROM beneficiaries WHERE id = ?");
$b_query->bind_param("i", $beneficiary_id);
$b_query->execute();
$b_result = $b_query->get_result()->fetch_assoc();

if (!$b_result) {
    echo json_encode(["error" => "Beneficiary not found"]);
    exit;
}

// Calculate age
$dob = new DateTime($b_result['dob']);
$age = $dob->diff(new DateTime())->y;

// Fetch eligible programs
$p_query = $conn->prepare("SELECT * FROM programs WHERE ? BETWEEN eligibility_age_min AND eligibility_age_max AND location = ?");
$p_query->bind_param("is", $age, $b_result['location']);
$p_query->execute();
$p_result = $p_query->get_result();

$eligible_programs = [];
while ($row = $p_result->fetch_assoc()) {
    $eligible_programs[] = $row;
}

echo json_encode($eligible_programs);
?>