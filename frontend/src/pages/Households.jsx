// src/pages/Households.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Households() {
  const [households, setHouseholds] = useState([]);

  useEffect(() => {
    client.get("/households").then((res) => setHouseholds(res.data));
  }, []);

  return (
    <div>
      <h2>Households</h2>
      <ul>
        {households.map((h) => (
          <li key={h.id}>{h.name} - {h.location}</li>
        ))}
      </ul>
    </div>
  );
}
