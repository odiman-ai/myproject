function updateStatus(enrollmentId, status) {
  fetch('update_enrollment_status.php', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({enrollment_id: enrollmentId, status: status})
  })
  .then(res => res.json())
  .then(response => {
    alert(response.status === 'success' ? 'Status updated!' : 'Error: ' + response.message);
    const id = document.getElementById('beneficiary_id').value;
    loadEnrollmentHistory(id);
  });
}
