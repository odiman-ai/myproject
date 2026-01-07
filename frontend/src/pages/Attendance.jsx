// src/pages/Attendance.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Attendance() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    client.get("/attendance").then((res) => setRecords(res.data));
  }, []);

  return (
    <div>
      <h2>Attendance</h2>
      <ul>
        {records.map((r) => (
          <li key={r.id}>
            {r.participant_name} - {r.activity_name} ({r.date})
          </li>
        ))}
      </ul>
    </div>
  );
}
