<?php
// Include database connection
require_once 'db_connect.php';

// Start HTML output
?>
<!DOCTYPE html>
<html>
<head>
    <title>Database Connection Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .success { 
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .error { 
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 20px;
            background: white;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        th { 
            background-color: #4CAF50; 
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        h1, h2, h3 {
            color: #333;
        }
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-success {
            background-color: #28a745;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Database Connection Test</h1>

<?php
// Check if connection exists
if (!isset($conn)) {
    echo '<div class="error">';
    echo '<h2>❌ Connection Error</h2>';
    echo '<p>Database connection variable is not set.</p>';
    echo '<p>Please check db_connect.php file.</p>';
    echo '</div>';
    echo '</div></body></html>';
    exit;
}

// Connection successful
echo '<div class="success">';
echo '<h2>✅ Database Connection Successful!</h2>';
echo '<p>Successfully connected to database: <strong>myproject_db</strong></p>';
echo '<p>Server: <strong>localhost</strong></p>';
echo '<p>Connection Type: <strong>PDO (PHP Data Objects)</strong></p>';
echo '</div>';

try {
    // Test 1: Count total users
    $stmt = $conn->query("SELECT COUNT(*) as count FROM users");
    $result = $stmt->fetch();
    $userCount = $result['count'];
    
    echo '<div class="info">';
    echo '<h3>📊 Database Statistics</h3>';
    echo '<p>Total users in database: <strong>' . $userCount . '</strong></p>';
    echo '</div>';
    
    // Test 2: Fetch all users
    if ($userCount > 0) {
        $stmt = $conn->query("SELECT id, username, email, full_name, phone, created_at FROM users ORDER BY id ASC");
        $users = $stmt->fetchAll();
        
        echo '<h3>👥 Users List</h3>';
        echo '<table>';
        echo '<thead>';
        echo '<tr>';
        echo '<th>ID</th>';
        echo '<th>Username</th>';
        echo '<th>Email</th>';
        echo '<th>Full Name</th>';
        echo '<th>Phone</th>';
        echo '<th>Created At</th>';
        echo '</tr>';
        echo '</thead>';
        echo '<tbody>';
        
        foreach($users as $user) {
            echo '<tr>';
            echo '<td><span class="badge badge-success">' . htmlspecialchars($user['id']) . '</span></td>';
            echo '<td>' . htmlspecialchars($user['username']) . '</td>';
            echo '<td>' . htmlspecialchars($user['email']) . '</td>';
            echo '<td>' . htmlspecialchars($user['full_name'] ?? 'N/A') . '</td>';
            echo '<td>' . htmlspecialchars($user['phone'] ?? 'N/A') . '</td>';
            echo '<td>' . htmlspecialchars($user['created_at']) . '</td>';
            echo '</tr>';
        }
        
        echo '</tbody>';
        echo '</table>';
    } else {
        echo '<div class="info">';
        echo '<h3>ℹ️ No Users Found</h3>';
        echo '<p>The users table exists but contains no data.</p>';
        echo '<p>You can add users by:</p>';
        echo '<ul>';
        echo '<li>Using the registration form on your main page</li>';
        echo '<li>Inserting data via phpMyAdmin</li>';
        echo '<li>Using the API endpoint: <code>api_add_user.php</code></li>';
        echo '</ul>';
        echo '</div>';
    }
    
    // Test 3: Show all tables in database
    echo '<h3>📋 Database Tables</h3>';
    $stmt = $conn->query("SHOW TABLES");
    $tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
    
    if (count($tables) > 0) {
        echo '<ul>';
        foreach($tables as $table) {
            echo '<li><strong>' . htmlspecialchars($table) . '</strong></li>';
        }
        echo '</ul>';
    }
    
} catch(PDOException $e) {
    echo '<div class="error">';
    echo '<h2>❌ Database Query Error</h2>';
    echo '<p><strong>Error Message:</strong> ' . htmlspecialchars($e->getMessage()) . '</p>';
    echo '<p><strong>Error Code:</strong> ' . $e->getCode() . '</p>';
    echo '<h3>Possible Solutions:</h3>';
    echo '<ul>';
    echo '<li>Check if the database tables exist in phpMyAdmin</li>';
    echo '<li>Verify table structure matches the queries</li>';
    echo '<li>Check database user permissions</li>';
    echo '</ul>';
    echo '</div>';
}
?>

        <div style="margin-top: 30px; padding: 15px; background-color: #e7f3ff; border-left: 4px solid #2196F3;">
            <h3>🔗 Quick Links</h3>
            <ul>
                <li><a href="http://localhost/phpmyadmin" target="_blank">Open phpMyAdmin</a></li>
                <li><a href="index.html">Go to Main Page</a></li>
                <li><a href="api_get_users.php" target="_blank">Test Get Users API</a></li>
                <li><a href="test_form.html">Test User Registration Form</a></li>
            </ul>
        </div>
    </div>
</body>
</html>