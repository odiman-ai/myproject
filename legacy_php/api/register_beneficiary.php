<?php
require 'db_connection.php';
header('Content-Type: application/json');

$data = json_decode(file_get_contents("php://input"), true);

$required = ['beneficiary_code', 'first_name', 'last_name', 'gender', 'village', 'parish', 'subcounty', 'district', 'created_by'];
foreach ($required as $field) {
    if (!isset($data[$field])) {
        echo json_encode(['status' => 'error', 'message' => "Missing field: $field"]);
        exit;
    }
}

$sql = "INSERT INTO beneficiaries (
  beneficiary_code, first_name, last_name, date_of_birth, gender, village, parish, subcounty, district,
  contact_phone, disability_status, vulnerability_category, relationship_to_household_head, marital_status,
  status, created_by
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

$stmt = $conn->prepare($sql);
$stmt->bind_param("ssssssssssssssss",
  $data['beneficiary_code'], $data['first_name'], $data['last_name'], $data['date_of_birth'],
  $data['gender'], $data['village'], $data['parish'], $data['subcounty'], $data['district'],
  $data['contact_phone'], $data['disability_status'], $data['vulnerability_category'],
  $data['relationship_to_household_head'], $data['marital_status'], $data['status'], $data['created_by']
);

if ($stmt->execute()) {
    echo json_encode(['status' => 'success', 'beneficiary_id' => $stmt->insert_id]);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Insert failed']);
}
$stmt->close();
$conn->close();
?>
