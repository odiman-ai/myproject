<?php
include 'db_config.php';

$sql = "SELECT * FROM beneficiaries";
$result = $conn->query($sql);

$beneficiaries = [];
while ($row = $result->fetch_assoc()) {
    $beneficiaries[] = $row;
}

echo json_encode($beneficiaries);
?>
