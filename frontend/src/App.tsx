// File: frontend/src/App.tsx
// Purpose: Root App component with ErrorBoundary, routes, and auth context
// Dependencies: react-router-dom, ./components/ErrorBoundary, ./components/AuthContext

import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { AuthProvider, useAuth } from "./components/AuthContext";

function Home() {
  return <div><h1>TAKA Platform</h1><p>Welcome to TAKA.</p></div>;
}

function Login() {
  return <div><h2>Login</h2><p>Login form placeholder.</p></div>;
}

function Register() {
  return <div><h2>Register</h2><p>Registration form placeholder.</p></div>;
}

function Dashboard() {
  const { user } = useAuth();
  return (
    <div>
      <h2>Dashboard</h2>
      {user ? <p>Welcome, {user.email}</p> : <p>Please log in.</p>}
    </div>
  );
}

function AdminUsers() {
  return <div><h2>Admin - Users</h2></div>;
}

function AdminTenants() {
  return <div><h2>Admin - Tenants</h2></div>;
}

function Nav() {
  const { user, logout } = useAuth();
  return (
    <nav style={{ padding: "1rem", background: "#333", color: "#fff" }}>
      <Link to="/" style={{ color: "#fff", marginRight: "1rem" }}>Home</Link>
      {!user && (
        <>
          <Link to="/login" style={{ color: "#fff", marginRight: "1rem" }}>Login</Link>
          <Link to="/register" style={{ color: "#fff", marginRight: "1rem" }}>Register</Link>
        </>
      )}
      {user && (
        <>
          <Link to="/dashboard" style={{ color: "#fff", marginRight: "1rem" }}>Dashboard</Link>
          <Link to="/admin/users" style={{ color: "#fff", marginRight: "1rem" }}>Users</Link>
          <Link to="/admin/tenants" style={{ color: "#fff", marginRight: "1rem" }}>Tenants</Link>
          <button onClick={logout}>Logout</button>
        </>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <div>
          <Nav />
          <main style={{ padding: "2rem" }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/admin/users" element={<AdminUsers />} />
              <Route path="/admin/tenants" element={<AdminTenants />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </ErrorBoundary>
  );
}
