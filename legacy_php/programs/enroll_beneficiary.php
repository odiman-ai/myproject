<?php
require 'db_connection.php';
header('Content-Type: application/json');

$data = json_decode(file_get_contents("php://input"), true);
if (!isset($data['beneficiary_id'], $data['program_id'], $data['status'])) {
    echo json_encode(['status' => 'error', 'message' => 'Missing fields']);
    exit;
}

$sql = "INSERT INTO enrollments (beneficiary_id, program_id, status, enrolled_at) VALUES (?, ?, ?, NOW())";
$stmt = $conn->prepare($sql);
$stmt->bind_param("iis", $data['beneficiary_id'], $data['program_id'], $data['status']);

if ($stmt->execute()) {
    echo json_encode(['status' => 'success', 'enrollment_id' => $stmt->insert_id]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Enrollment failed']);
}
$stmt->close();
$conn->close();
?>
