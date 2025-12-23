<?php
$mysqli = new mysqli(
  'spms-db.cqh8eucws0g2.us-east-1.rds.amazonaws.com',
  'admin',
  'YourStrongPassword',
  'spms_db',
  3306
);

if ($mysqli->connect_error) {
  die("❌ Connection failed: " . $mysqli->connect_error);
} else {
  echo "✅ Connected successfully to RDS!";
}

$result = $mysqli->query("SELECT NOW() AS current_time");
$row = $result->fetch_assoc();
echo "<br>Database time: " . $row['current_time'];
?>
