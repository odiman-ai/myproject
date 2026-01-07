// src/pages/Reports.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Reports() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    client.get("/reports").then((res) => setReports(res.data));
  }, []);

  return (
    <div>
      <h2>Reports</h2>
      <ul>
        {reports.map((r) => (
          <li key={r.id}>
            {r.title} - {r.date}
          </li>
        ))}
      </ul>
    </div>
  );
}
