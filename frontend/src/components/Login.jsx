// src/components/Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setAuthTokens } from "../api.js";

/**
 * Minimal Login component
 *
 * Props:
 * - onLogin(result) optional callback. Called with tokens object { access_token, refresh_token, expires_in }
 *
 * Behavior:
 * - Calls api.login(username, password)
 * - Persists tokens via setAuthTokens
 * - Calls onLogin(tokens) if provided
 * - Redirects to "/" on success
 */
export default function Login({ onLogin = null }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const tokens = await login(username, password);
      // Persist tokens in api module and localStorage
      setAuthTokens(tokens.access_token, tokens.refresh_token || null, tokens.expires_in ? Date.now() + tokens.expires_in * 1000 : null);

      // Notify parent if provided
      if (typeof onLogin === "function") {
        try {
          await onLogin(tokens);
        } catch {
          // ignore parent handler errors
        }
      }

      // Redirect to dashboard
      navigate("/");
    } catch (err) {
      const msg = err?.message || "Login failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={container}>
      <h2 style={{ margin: 0 }}>Sign in</h2>

      <form onSubmit={handleSubmit} style={form}>
        <label style={label}>
          Username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={input}
            autoComplete="username"
          />
        </label>

        <label style={label}>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={input}
            autoComplete="current-password"
          />
        </label>

        <label style={checkboxLabel}>
          <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
          Remember me
        </label>

        {error && <div style={errorStyle}>{error}</div>}

        <div style={{ display: "flex", gap: 8 }}>
          <button type="submit" style={buttonPrimary} disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </div>
      </form>
    </div>
  );
}

/* Styles */
const container = {
  maxWidth: 420,
  margin: "2rem auto",
  padding: "1.25rem",
  border: "1px solid #e6e6e6",
  borderRadius: 8,
  background: "#fff",
};

const form = {
  display: "flex",
  flexDirection: "column",
  gap: 12,
  marginTop: 12,
};

const label = {
  display: "flex",
  flexDirection: "column",
  fontSize: 14,
};

const input = {
  padding: "8px 10px",
  fontSize: 14,
  borderRadius: 4,
  border: "1px solid #ccc",
  marginTop: 6,
};

const checkboxLabel = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  fontSize: 13,
};

const buttonPrimary = {
  padding: "10px 14px",
  background: "#0b5fff",
  color: "#fff",
  border: "none",
  borderRadius: 6,
  cursor: "pointer",
};

const errorStyle = {
  color: "#b91c1c",
  background: "#fee2e2",
  padding: "8px",
  borderRadius: 6,
  fontSize: 13,
};
