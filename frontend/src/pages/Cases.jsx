// src/pages/Cases.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Cases() {
  const [cases, setCases] = useState([]);

  useEffect(() => {
    client.get("/cases").then((res) => setCases(res.data));
  }, []);

  return (
    <div>
      <h2>Case Management</h2>
      <ul>
        {cases.map((c) => (
          <li key={c.id}>
            {c.case_number} - {c.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
