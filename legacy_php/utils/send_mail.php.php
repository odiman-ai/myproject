<?php
include 'db_config.php';

$to = "manager@example.com";
$subject = "New Enrollment Pending Approval";
$message = "A new enrollment has been submitted and is pending your review.";

mail($to, $subject, $message);
?>
