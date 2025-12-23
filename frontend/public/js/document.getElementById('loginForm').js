document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());

  fetch('login.php', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(response => {
    if (response.status === 'success') {
      alert('Logged in as ' + response.role);
      sessionStorage.setItem('role', response.role);
      showSections(response.role);
    } else {
      alert(response.message);
    }
  });
});
