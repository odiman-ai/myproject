function logout() {
  fetch('logout.php')
    .then(() => {
      sessionStorage.clear();
      alert('Logged out');
      location.reload();
    });
}
