<?php
require 'db_connection.php';
header('Content-Type: application/json');

// Get action from query string
$action = isset($_GET['action']) ? $_GET['action'] : '';
$data = json_decode(file_get_contents("php://input"), true);

switch ($action) {

    // 🧍 Register Beneficiary
    case 'register_beneficiary':
        $sql = "INSERT INTO beneficiaries (
          beneficiary_code, first_name, last_name, date_of_birth, gender, village, parish, subcounty, district,
          contact_phone, disability_status, vulnerability_category, relationship_to_household_head, marital_status,
          status, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ssssssssssssssss",
          $data['beneficiary_code'], $data['first_name'], $data['last_name'], $data['date_of_birth'],
          $data['gender'], $data['village'], $data['parish'], $data['subcounty'], $data['district'],
          $data['contact_phone'], $data['disability_status'], $data['vulnerability_category'],
          $data['relationship_to_household_head'], $data['marital_status'], $data['status'], $data['created_by']
        );
        $stmt->execute();
        echo json_encode(['status'=>'success','beneficiary_id'=>$stmt->insert_id]);
        $stmt->close();
        break;

    // 📚 Enroll Beneficiary
    case 'enroll_beneficiary':
        $sql = "INSERT INTO enrollments (beneficiary_id, program_id, status, enrolled_at) VALUES (?, ?, ?, NOW())";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("iis", $data['beneficiary_id'], $data['program_id'], $data['status']);
        $stmt->execute();
        echo json_encode(['status'=>'success','enrollment_id'=>$stmt->insert_id]);
        $stmt->close();
        break;

    // 🕒 Submit Attendance
    case 'submit_attendance':
        $sql = "INSERT INTO attendance (beneficiary_id, check_in_method, location_lat, location_lng, recorded_by, notes, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("issddsi",
          $data['beneficiary_id'], $data['check_in_method'], $data['location_lat'], $data['location_lng'],
          $data['recorded_by'], $data['notes'], $data['synced']
        );
        $stmt->execute();
        echo json_encode(['status'=>'success','attendance_id'=>$stmt->insert_id]);
        $stmt->close();
        break;

    // 📝 Submit Survey
    case 'submit_survey':
        $sql = "INSERT INTO surveys (beneficiary_id, question, response) VALUES (?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("iss", $data['beneficiary_id'], $data['question'], $data['response']);
        $stmt->execute();
        echo json_encode(['status'=>'success','survey_id'=>$stmt->insert_id]);
        $stmt->close();
        break;

    // 🔔 Get Notifications
    case 'get_notifications':
        $user_id = intval($_GET['user_id']);
        $sql = "SELECT id, title, message, type, is_read, action_url, created_at 
                FROM notifications WHERE user_id = ? ORDER BY created_at DESC";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("i", $user_id);
        $stmt->execute();
        $result = $stmt->get_result();
        $notifications = [];
        while ($row = $result->fetch_assoc()) {
            $notifications[] = $row;
        }
        echo json_encode(['status'=>'success','notifications'=>$notifications]);
        $stmt->close();
        break;

    default:
        echo json_encode(['status'=>'error','message'=>'Invalid action']);
}
$conn->close();
?>
