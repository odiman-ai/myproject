// src/pages/DebugPage.jsx
import React from "react";
import TestRunner from "../components/TestRunner"; // relative path from pages to components

export default function DebugPage() {
  return (
    <div style={{ padding: 20 }}>
      <h1>Debug Tools</h1>
      <TestRunner />
    </div>
  );
}
