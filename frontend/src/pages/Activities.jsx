// src/pages/Activities.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Activities() {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    client.get("/activities").then((res) => setActivities(res.data));
  }, []);

  return (
    <div>
      <h2>Activities</h2>
      <ul>
        {activities.map((a) => (
          <li key={a.id}>{a.name} - {a.date}</li>
        ))}
      </ul>
    </div>
  );
}
