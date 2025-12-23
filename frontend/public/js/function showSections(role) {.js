function showSections(role) {
  document.querySelectorAll('section').forEach(s => s.style.display = 'none');
  document.getElementById('loginForm').parentElement.style.display = 'none';

  if (role === 'staff') {
    document.querySelectorAll('section')[1].style.display = 'block'; // Beneficiary
    document.querySelectorAll('section')[3].style.display = 'block'; // Enrollment
  } else if (role === 'manager') {
    document.querySelectorAll('section')[3].style.display = 'block'; // Enrollment
    // Add approval section later
  } else if (role === 'admin') {
    document.querySelectorAll('section').forEach(s => s.style.display = 'block');
  }
}
