<?php
// Database configuration
$host = 'localhost';
$dbname = 'myproject_db';  // Make sure this matches your database name
$username = 'root';
$password = ''; // Empty for default XAMPP

// Create connection using PDO
try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    // Set error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $conn->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    // Don't output success message here - let calling scripts handle it
} catch(PDOException $e) {
    // Log error but don't expose details in production
    error_log("Database connection error: " . $e->getMessage());
    die("Database connection failed. Please check server logs.");
}
?>