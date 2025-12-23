<?php
require 'db_connection.php'; // your DB config file

header('Content-Type: application/json');

// Read JSON input
$data = json_decode(file_get_contents("php://input"), true);

// Validate required fields
if (!isset($data['beneficiary_id'], $data['question'], $data['response'])) {
    echo json_encode(['status' => 'error', 'message' => 'Missing required fields']);
    exit;
}

$beneficiary_id = intval($data['beneficiary_id']);
$question = trim($data['question']);
$response = trim($data['response']);

// Prepare and execute