// src/components/TestRunner.jsx
import React, { useState } from "react";
import { login, setAuthTokens } from "../api.js";

/**
 * TestRunner
 * - Editable fields for participant payload
 * - Preset test cases selectable from a dropdown
 * - Buttons to run selected test or run all presets
 * - On-screen log of steps and responses
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";

const PRESETS = {
  happy: {
    name: "Happy Path",
    payload: {
      name: "Test Participant",
      gender: "female",
      age: 28,
      location: "Kampala",
      national_id: `TP-${Date.now()}`,
      custom_fields: [{ field_id: 1, value: "example" }],
    },
  },
  missingName: {
    name: "Missing Name",
    payload: {
      name: "",
      gender: "female",
      age: 28,
      location: "Kampala",
      national_id: `TP-${Date.now()}`,
    },
  },
  invalidEmail: {
    name: "Invalid Email",
    payload: {
      name: "Bad Email",
      gender: "male",
      age: 30,
      location: "Gulu",
      national_id: `TP-${Date.now()}`,
      email: "not-an-email",
    },
  },
  duplicateId: {
    name: "Duplicate National ID",
    payload: {
      name: "Duplicate ID",
      gender: "male",
      age: 40,
      location: "Mbale",
      national_id: "DUPLICATE-12345",
    },
  },
};

async function registerParticipant(payload, token) {
  const resp = await fetch(`${API_BASE}/participants`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  const data = await resp.json().catch(() => null);
  return { ok: resp.ok, status: resp.status, data };
}

export default function TestRunner() {
  const [log, setLog] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState("happy");
  const [payload, setPayload] = useState(PRESETS.happy.payload);
  const [running, setRunning] = useState(false);

  const append = (line) => setLog((l) => [line, ...l]);

  function applyPreset(key) {
    const preset = PRESETS[key];
    if (!preset) return;
    setSelectedPreset(key);
    // clone to avoid shared reference
    setPayload(JSON.parse(JSON.stringify(preset.payload)));
    append(`Applied preset: ${preset.name}`);
  }

  function updateField(path, value) {
    // path is dot-separated, e.g., "custom_fields.0.value"
    const parts = path.split(".");
    const next = { ...payload };
    let cur = next;
    for (let i = 0; i < parts.length - 1; i++) {
      const p = parts[i];
      if (!(p in cur)) cur[p] = {};
      cur = cur[p];
    }
    cur[parts[parts.length - 1]] = value;
    setPayload(next);
  }

  async function runSelected() {
    setRunning(true);
    append("Starting test: " + (PRESETS[selectedPreset]?.name || "Custom"));
    try {
      // 1. Login as admin
      const auth = await login("admin", "admin123");
      setAuthTokens(auth.access_token, auth.refresh_token, Date.now() + (auth.expires_in || 3600) * 1000);
      append("Logged in as admin");

      // 2. Register participant
      const res = await registerParticipant(payload, auth.access_token);
      append(`Register response: ${res.status} ${JSON.stringify(res.data)}`);

      // 3. Enroll if created
      if (res.ok && res.data && res.data.id) {
        const enrollResp = await fetch(`${API_BASE}/enrollments`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${auth.access_token}`,
          },
          body: JSON.stringify({
            beneficiary_id: res.data.id,
            program_id: 1,
            enrollment_date: new Date().toISOString().slice(0, 10),
          }),
        });
        append(`Enroll response: ${enrollResp.status}`);
      }
    } catch (err) {
      append(`Error: ${err?.message || err}`);
    } finally {
      setRunning(false);
    }
  }

  async function runAllPresets() {
    for (const key of Object.keys(PRESETS)) {
      applyPreset(key);
      // small delay to allow UI update
       
      await new Promise((r) => setTimeout(r, 200));
       
      await runSelected();
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h3>Frontend Test Runner</h3>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <select value={selectedPreset} onChange={(e) => applyPreset(e.target.value)} style={{ padding: 8 }}>
          {Object.entries(PRESETS).map(([k, v]) => (
            <option key={k} value={k}>
              {v.name}
            </option>
          ))}
          <option value="custom">Custom</option>
        </select>

        <button onClick={runSelected} disabled={running} style={button}>
          {running ? "Running…" : "Run Selected"}
        </button>

        <button onClick={runAllPresets} disabled={running} style={buttonSecondary}>
          Run All Presets
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
        <div>
          <h4>Editable Payload</h4>

          <label style={label}>
            Name
            <input value={payload.name || ""} onChange={(e) => updateField("name", e.target.value)} style={input} />
          </label>

          <label style={label}>
            Gender
            <input value={payload.gender || ""} onChange={(e) => updateField("gender", e.target.value)} style={input} />
          </label>

          <label style={label}>
            Age
            <input type="number" value={payload.age || ""} onChange={(e) => updateField("age", Number(e.target.value))} style={input} />
          </label>

          <label style={label}>
            Location
            <input value={payload.location || ""} onChange={(e) => updateField("location", e.target.value)} style={input} />
          </label>

          <label style={label}>
            National ID
            <input value={payload.national_id || ""} onChange={(e) => updateField("national_id", e.target.value)} style={input} />
          </label>

          <label style={label}>
            Email (optional)
            <input value={payload.email || ""} onChange={(e) => updateField("email", e.target.value)} style={input} />
          </label>
        </div>

        <div>
          <h4>Custom Fields (first item editable)</h4>
          <label style={label}>
            Custom Field 0 - field_id
            <input
              type="number"
              value={(payload.custom_fields && payload.custom_fields[0] && payload.custom_fields[0].field_id) || ""}
              onChange={(e) => {
                const val = Number(e.target.value);
                const next = { ...payload };
                next.custom_fields = next.custom_fields || [];
                next.custom_fields[0] = next.custom_fields[0] || {};
                next.custom_fields[0].field_id = val;
                setPayload(next);
              }}
              style={input}
            />
          </label>

          <label style={label}>
            Custom Field 0 - value
            <input
              value={(payload.custom_fields && payload.custom_fields[0] && payload.custom_fields[0].value) || ""}
              onChange={(e) => {
                const val = e.target.value;
                const next = { ...payload };
                next.custom_fields = next.custom_fields || [];
                next.custom_fields[0] = next.custom_fields[0] || {};
                next.custom_fields[0].value = val;
                setPayload(next);
              }}
              style={input}
            />
          </label>

          <div style={{ marginTop: 12 }}>
            <h4>Raw JSON</h4>
            <textarea
              value={JSON.stringify(payload, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setPayload(parsed);
                } catch {
                  // ignore parse errors while editing
                }
              }}
              style={{ width: "100%", height: 200, fontFamily: "monospace", padding: 8 }}
            />
          </div>
        </div>
      </div>

      <div style={{ maxHeight: 300, overflow: "auto", background: "#f7f7f7", padding: 8 }}>
        {log.map((l, i) => (
          <div key={i} style={{ fontFamily: "monospace", marginBottom: 6 }}>
            {l}
          </div>
        ))}
      </div>
    </div>
  );
}

/* Styles */
const label = { display: "flex", flexDirection: "column", marginBottom: 8, fontSize: 13 };
const input = { padding: 8, borderRadius: 4, border: "1px solid #ccc", marginTop: 6 };
const button = { padding: "8px 12px", background: "#0b5fff", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" };
const buttonSecondary = { padding: "8px 12px", background: "#f3f4f6", color: "#111", border: "none", borderRadius: 6, cursor: "pointer" };
