<?php
include 'db_config.php'; // contains DB connection

$data = json_decode(file_get_contents("php://input"), true);

$name = $data['name'];
$dob = $data['dob'];
$gender = $data['gender'];
$location = $data['location'];
$program_id = $data['program_id'];

$sql = "INSERT INTO beneficiaries (name, dob, gender, location, program_id)
        VALUES (?, ?, ?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssssi", $name, $dob, $gender, $location, $program_id);

if ($stmt->execute()) {
    echo json_encode(["status" => "success"]);
} else {
    echo json_encode(["status" => "error", "message" => $stmt->error]);
}
?>