// frontend/src/services/authService.js
// Simple localStorage-backed auth helper

export const authService = {
  getToken: () => localStorage.getItem('access_token'),
  setToken: (token) => localStorage.setItem('access_token', token),
  clearToken: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
  isAuthenticated: () => {
    const t = localStorage.getItem('access_token');
    return !!t && t.length > 10;
  },
};
