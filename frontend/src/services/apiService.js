// frontend/src/services/apiService.js
import { authService } from './authService';

export const API_BASE_URL = 'http://localhost:8000'; // keep consistent with backend

export const apiService = {
  async request(endpoint, options = {}) {
    const token = authService.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 explicitly
    if (res.status === 401) {
      authService.clearToken();
      // reload to force login UI; optional in your app
      window.location.reload();
      throw new Error('Not authenticated');
    }

    // Safely parse body (may be empty or non-JSON)
    const text = await res.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (err) {
      data = text;
    }

    if (!res.ok) {
      const message = data && data.detail ? data.detail : (typeof data === 'string' ? data : 'Request failed');
      throw new Error(message);
    }

    return data;
  },

  async login(username, password) {
    // Try OAuth2-style form first (common with FastAPI)
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    const text = await response.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }

    if (!response.ok) {
      const msg = data && data.detail ? data.detail : (typeof data === 'string' ? data : 'Login failed');
      throw new Error(msg);
    }

    if (!data || !data.access_token) {
      throw new Error('Login succeeded but no access token returned');
    }

    authService.setToken(data.access_token);

    // Fetch profile
    const user = await this.request('/api/v1/auth/me');
    authService.setUser(user);
    return user;
  },

  async logout() {
    try {
      // request will include Authorization header if token exists
      await this.request('/api/v1/auth/logout', { method: 'POST' });
    } catch (error) {
      // ignore network errors but clear local state anyway
      console.warn('Logout error (ignored):', error?.message || error);
    } finally {
      authService.clearToken();
    }
  },

  async checkHealth() {
    return await this.request('/api/v1/health');
  },
};
