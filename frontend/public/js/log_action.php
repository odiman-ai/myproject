<?php
include 'db_config.php';
session_start();

$user_id = $_SESSION['user_id'] ?? null;
$action = $_POST['action'];
$details = $_POST['details'];

if ($user_id) {
    $sql = "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("iss", $user_id, $action, $details);
    $stmt->execute();
}
?>
