<?php
include 'db_config.php';

$data = json_decode(file_get_contents("php://input"), true);
$username = $data['username'];
$password = password_hash($data['password'], PASSWORD_DEFAULT);
$role = $data['role'];

$sql = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("sss", $username, $password, $role);

echo json_encode($stmt->execute() ? ["status" => "success"] : ["status" => "error", "message" => $stmt->error]);
?>
