// src/App.jsx
import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";

import AdminDashboard from "./components/AdminDashboard";
import DebugPage from "./pages/DebugPage";
import Login from "./components/Login";
import {
  loadAuthTokensFromStorage,
  setAuthTokens,
  clearAuthTokens,
  getCurrentUser,
  refreshAccessToken,
} from "./api.js";

/**
 * AuthContext provides: currentUser, loading, loginSuccess(user, tokens), logout()
 * Components can call useAuth() to access auth state and actions.
 */
const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initializing, setInitializing] = useState(true);

  // Initialize tokens from storage and try to fetch current user
  useEffect(() => {
    async function init() {
      setInitializing(true);
      const tokens = loadAuthTokensFromStorage();
      if (tokens && tokens.access_token) {
        try {
          const user = await getCurrentUser();
          setCurrentUser(user);
        } catch (err) {
          // Try to refresh token once if available
          try {
            const refreshed = await refreshAccessToken();
            if (refreshed && refreshed.access_token) {
              setAuthTokens(refreshed.access_token, refreshed.refresh_token || null, refreshed.expires_in ? Date.now() + refreshed.expires_in * 1000 : null);
              const user = await getCurrentUser();
              setCurrentUser(user);
            } else {
              clearAuthTokens();
              setCurrentUser(null);
            }
          } catch {
            clearAuthTokens();
            setCurrentUser(null);
          }
        }
      }
      setLoading(false);
      setInitializing(false);
    }
    init();
  }, []);

  // Called by Login component after successful login
  const loginSuccess = useCallback(async (tokens) => {
    // tokens: { access_token, refresh_token, expires_in }
    setAuthTokens(tokens.access_token, tokens.refresh_token || null, tokens.expires_in ? Date.now() + tokens.expires_in * 1000 : null);
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      return user;
    } catch (err) {
      // If fetching user fails, clear tokens and rethrow
      clearAuthTokens();
      setCurrentUser(null);
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      // call backend logout if needed (api.logout) — but keep it optional here
      clearAuthTokens();
      setCurrentUser(null);
    } catch {
      clearAuthTokens();
      setCurrentUser(null);
    }
  }, []);

  // Optional: automatic token refresh before expiry (simple interval)
  useEffect(() => {
    let interval = null;
    // Refresh every 10 minutes if user is logged in
    if (currentUser) {
      interval = setInterval(async () => {
        try {
          await refreshAccessToken();
        } catch {
          // ignore refresh errors; user will re-authenticate when needed
        }
      }, 10 * 60 * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentUser]);

  const value = {
    currentUser,
    loading,
    initializing,
    loginSuccess,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/* Simple protected route wrapper */
function RequireAuth({ children }) {
  const auth = useAuth();
  if (auth.initializing) return <div>Loading...</div>;
  if (auth.loading) return <div>Loading user...</div>;
  return auth.currentUser ? children : <Navigate to="/login" replace />;
}

/* Minimal top navigation */
function TopNav() {
  const auth = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await auth.logout();
    navigate("/login");
  }

  return (
    <nav style={navStyle}>
      <div style={{ display: "flex", gap: 12 }}>
        <Link to="/" style={linkStyle}>Dashboard</Link>
        <Link to="/debug" style={linkStyle}>Debug</Link>
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        {auth.currentUser ? (
          <>
            <span style={{ color: "#111", fontSize: 14 }}>{auth.currentUser.username}</span>
            <button onClick={handleLogout} style={buttonStyle}>Logout</button>
          </>
        ) : (
          <Link to="/login" style={linkStyle}>Login</Link>
        )}
      </div>
    </nav>
  );
}

/* App component with routes */
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <TopNav />
        <div style={{ padding: 16 }}>
          <Routes>
            <Route
              path="/"
              element={
                <RequireAuth>
                  <AdminDashboard />
                </RequireAuth>
              }
            />

            <Route
              path="/debug"
              element={
                <RequireAuth>
                  <DebugPage />
                </RequireAuth>
              }
            />

            <Route
              path="/login"
              element={<LoginWrapper />}
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

/* Login wrapper to integrate with AuthContext and redirect on success */
function LoginWrapper() {
  const auth = useAuth();
  const navigate = useNavigate();

  async function handleLogin(user) {
    // Called by Login component when it has fetched tokens and optionally user
    // If Login component returns tokens instead, call auth.loginSuccess(tokens)
    // Here we assume Login component calls api.login and then calls auth.loginSuccess itself via props
    // For compatibility, we accept either a user object or tokens object
    if (!user) return;
    // If user is an object with username, treat as currentUser already set
    if (user.username) {
      navigate("/");
      return;
    }
    // If user contains tokens, call loginSuccess
    if (user.access_token) {
      try {
        await auth.loginSuccess(user);
        navigate("/");
      } catch {
        // ignore and let Login show error
      }
    }
  }

  return <Login onLogin={handleLogin} />;
}

/* Styles */
const navStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
  padding: "12px 16px",
  borderBottom: "1px solid #e6e6e6",
  background: "#fafafa",
};

const linkStyle = {
  textDecoration: "none",
  color: "#0b5fff",
  fontWeight: 500,
};

const buttonStyle = {
  padding: "6px 10px",
  borderRadius: 6,
  border: "1px solid #e6e6e6",
  background: "#fff",
  cursor: "pointer",
};
