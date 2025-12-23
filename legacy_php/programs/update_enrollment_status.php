<?php
include 'db_config.php';

$data = json_decode(file_get_contents("php://input"), true);
$enrollment_id = $data['enrollment_id'];
$status = $data['status'];

$sql = "UPDATE enrollments SET status = ? WHERE id = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("si", $status, $enrollment_id);

echo json_encode($stmt->execute() ? ["status" => "success"] : ["status" => "error", "message" => $stmt->error]);
?>