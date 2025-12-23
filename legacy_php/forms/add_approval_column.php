<?php
include 'db_config.php';

$sql = "ALTER TABLE enrollments ADD COLUMN approved_by INT DEFAULT NULL";

if ($conn->query($sql) === TRUE) {
    echo "Column 'approved_by' added successfully.";
} else {
    echo "Error: " . $conn->error;
}
?>
