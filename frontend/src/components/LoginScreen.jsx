// frontend/src/components/LoginScreen.jsx
import React, { useState } from 'react';
import { apiService } from '../services/apiService';

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('admin'); // dev default
  const [password, setPassword] = useState('admin123'); // dev default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await apiService.login(username, password);
      onLogin();
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded shadow">
        <h2 className="text-2xl font-semibold mb-4">SPMS Login</h2>
        {error && <div className="mb-4 text-red-600">{error}</div>}
        <form onSubmit={handleSubmit}>
          <label className="block mb-2 text-sm font-medium">Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 border rounded mb-4"
            placeholder="Enter username"
            autoFocus
          />
          <label className="block mb-2 text-sm font-medium">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded mb-4"
            placeholder="Enter password"
            onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
          />
          <button
            type="submit"
            className="w-full py-2 bg-blue-600 text-white rounded disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <div className="mt-4 text-sm text-gray-500">
          Default credentials: <strong>admin / admin123</strong>
        </div>
      </div>
    </div>
  );
}
