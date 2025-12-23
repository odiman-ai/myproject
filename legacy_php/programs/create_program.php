<?php
include 'db_config.php';

$data = json_decode(file_get_contents("php://input"), true);

$sql = "INSERT INTO programs (name, description, eligibility_age_min, eligibility_age_max, location, income_threshold)
        VALUES (?, ?, ?, ?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssiisd", $data['name'], $data['description'], $data['eligibility_age_min'], $data['eligibility_age_max'], $data['location'], $data['income_threshold']);

echo json_encode($stmt->execute() ? ["status" => "success"] : ["status" => "error", "message" => $stmt->error]);
?>
