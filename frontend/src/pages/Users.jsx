import { useEffect, useState } from "react";
import client from "../api/client";

export default function Users() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    client.get("/users").then((res) => setUsers(res.data));
  }, []);

  return (
    <div>
      <h2>Users</h2>
      <ul>
        {users.map((u) => (
          <li key={u.id}>{u.username} ({u.role})</li>
        ))}
      </ul>
    </div>
  );
}
