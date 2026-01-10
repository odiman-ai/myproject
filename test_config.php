<?php
$conn = mysqli_connect("localhost", "root", "", "test");

if ($conn) {
    echo "✅ Connected successfully!\n";
    
    $result = mysqli_query($conn, "SHOW VARIABLES LIKE 'innodb_buffer_pool_size'");
    $row = mysqli_fetch_assoc($result);
    echo "Buffer Pool Size: " . ($row['Value'] / 1024 / 1024) . " MB\n";
    
    mysqli_close($conn);
} else {
    echo "❌ Connection failed: " . mysqli_connect_error();
}
?>