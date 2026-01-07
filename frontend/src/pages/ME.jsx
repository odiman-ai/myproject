// src/pages/ME.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function ME() {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    client.get("/me").then((res) => setIndicators(res.data));
  }, []);

  return (
    <div>
      <h2>Monitoring & Evaluation Indicators</h2>
      <ul>
        {indicators.map((i) => (
          <li key={i.id}>
            {i.name}: {i.value}
          </li>
        ))}
      </ul>
    </div>
  );
}
