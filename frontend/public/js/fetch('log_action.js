fetch('log_action.php', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: new URLSearchParams({
    action: 'Enroll Beneficiary',
    details: `Beneficiary ID ${beneficiaryId} enrolled into Program ID ${programId}`
  })
});
