// src/pages/Surveys.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Surveys() {
  const [surveys, setSurveys] = useState([]);

  useEffect(() => {
    client.get("/surveys").then((res) => setSurveys(res.data));
  }, []);

  return (
    <div>
      <h2>Surveys</h2>
      <ul>
        {surveys.map((s) => (
          <li key={s.id}>
            {s.title} - {s.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
