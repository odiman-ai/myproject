// src/pages/Projects.jsx
import { useEffect, useState } from "react";
import client from "../api/client";

export default function Projects() {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    client.get("/projects").then((res) => setProjects(res.data));
  }, []);

  return (
    <div>
      <h2>Projects</h2>
      <ul>
        {projects.map((p) => (
          <li key={p.id}>{p.title} ({p.status})</li>
        ))}
      </ul>
    </div>
  );
}
