// Register new user
async function registerUser(username, email, password) {
    try {
        const response = await fetch('register.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Fetch all users
async function getUsers() {
    try {
        const response = await fetch('get_users.php');
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example usage
document.getElementById('registerBtn').addEventListener('click', () => {
    registerUser('johndoe', 'john@example.com', 'password123');
});

document.getElementById('loadUsersBtn').addEventListener('click', async () => {
    const result = await getUsers();
    if (result.success) {
        displayUsers(result.data);
    }
});

function displayUsers(users) {
    const container = document.getElementById('usersContainer');
    container.innerHTML = users.map(user => `
        <div class="user-card">
            <h3>${user.username}</h3>
            <p>${user.email}</p>
            <small>${user.created_at}</small>
        </div>
    `).join('');
}