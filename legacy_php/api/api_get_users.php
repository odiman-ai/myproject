<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Include database connection
include 'db_connect.php';

try {
    // Query to get all users
    $sql = "SELECT id, username, email, full_name, phone, created_at FROM users ORDER BY created_at DESC";
    $stmt = $conn->prepare($sql);
    $stmt->execute();
    
    $users = $stmt->fetchAll();
    
    // Return success response
    echo json_encode([
        'success' => true,
        'data' => $users,
        'count' => count($users),
        'message' => 'Users retrieved successfully'
    ]);
    
} catch(PDOException $e) {
    // Return error response
    echo json_encode([
        'success' => false,
        'message' => 'Error retrieving users: ' . $e->getMessage(),
        'data' => []
    ]);
}
?>