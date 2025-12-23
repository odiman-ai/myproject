<?php
$conn = new mysqli(
  'spms-db.xxxxx.rds.amazonaws.com', // RDS endpoint
  'admin',                           // DB user
  'YourPasswordHere',                // DB password
  'spms_db'                          // DB name
);

if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
?>
