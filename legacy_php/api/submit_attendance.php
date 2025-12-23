<?php
require 'db_connection.php';
header('Content-Type: application/json');

$data = json_decode(file_get_contents("php://input"), true);
if (!isset($data['beneficiary_id'], $data['check_in_method'], $data['recorded_by'])) {
    echo json_encode(['status' => 'error', 'message' => 'Missing fields']);
    exit;
}

$sql = "INSERT INTO attendance (beneficiary_id, check_in_method, location_lat, location_lng, recorded_by, notes, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("issddsi",
  $data['beneficiary_id'], $data['check_in_method'], $data['location_lat'], $data['location_lng'],
  $data['recorded_by'], $data['notes'], $data['synced']
);

if ($stmt->execute()) {
    echo json_encode(['status' => 'success', 'attendance_id' => $stmt->insert_id]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Attendance failed']);
}
$stmt->close();
$conn->close();
?>
