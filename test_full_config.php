<?php
echo "=== MySQL Configuration Test ===\n\n";

$conn = mysqli_connect("localhost", "root", "", "test");

if ($conn) {
    echo "✅ Connected successfully!\n\n";
    
    $checks = [
        'innodb_buffer_pool_size' => 'Buffer Pool Size',
        'max_allowed_packet' => 'Max Allowed Packet',
        'character_set_server' => 'Character Set',
        'key_buffer_size' => 'Key Buffer Size',
        'sort_buffer_size' => 'Sort Buffer Size'
    ];
    
    foreach ($checks as $var => $label) {
        $result = mysqli_query($conn, "SHOW VARIABLES LIKE '$var'");
        $row = mysqli_fetch_assoc($result);
        
        if (in_array($var, ['character_set_server'])) {
            echo "$label: " . $row['Value'] . "\n";
        } else {
            echo "$label: " . ($row['Value'] / 1024 / 1024) . " MB\n";
        }
    }
    
    mysqli_close($conn);
} else {
    echo "❌ Connection failed: " . mysqli_connect_error();
}
?>