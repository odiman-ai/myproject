// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

// Pages
import Login from "./pages/Login";
import Users from "./pages/Users";
import Households from "./pages/Households";
import Projects from "./pages/Projects";
import Activities from "./pages/Activities";
import Attendance from "./pages/Attendance";
import Surveys from "./pages/Surveys";
import ME from "./pages/ME";
import Reports from "./pages/Reports";
import Cases from "./pages/Cases";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/users" element={<Users />} />
          <Route path="/households" element={<Households />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/activities" element={<Activities />} />
          <Route path="/attendance" element={<Attendance />} />
          <Route path="/surveys" element={<Surveys />} />
          <Route path="/me" element={<ME />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/cases" element={<Cases />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
