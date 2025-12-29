import React, { useEffect, useState } from 'react';
import { authService } from './services/authService';
import { apiService } from './services/apiService';
import LoginScreen from './components/LoginScreen';
import Dashboard from './components/Dashboard';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [user, setUser] = useState(authService.getUser());
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Sync auth state on mount (useful if token was set in another tab)
  useEffect(() => {
    const init = async () => {
      setCheckingAuth(true);
      try {
        if (authService.isAuthenticated()) {
          // Try to refresh user profile; if token invalid this will clear it
          const profile = await apiService.request('/api/v1/auth/me');
          authService.setUser(profile);
          setUser(profile);
          setIsAuthenticated(true);
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (err) {
        // token invalid or network error — ensure clean state
        authService.clearToken();
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    init();

    // Optional: listen for storage events to sync auth across tabs
    const onStorage = (e) => {
      if (e.key === 'access_token') {
        setIsAuthenticated(!!localStorage.getItem('access_token'));
        setUser(authService.getUser());
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const handleLogin = () => {
    // After successful login, authService already stores token and user
    setUser(authService.getUser());
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      // call backend logout to revoke tokens if implemented
      await apiService.logout();
    } catch (err) {
      // ignore network errors but clear local state anyway
      console.warn('Logout error:', err?.message || err);
    } finally {
      authService.clearToken();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Checking authentication…</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return <Dashboard user={user} onLogout={handleLogout} />;
}
