// File: frontend/src/App.tsx
// Purpose: Root App component with ErrorBoundary, routes, and auth context

import { FC } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { AuthProvider, useAuth } from "./components/AuthContext";
import DocumentUpload from "./components/documents/DocumentUpload";
import MemorySearch from "./components/memory/MemorySearch";
import HILDashboard from "./components/hil/HILDashboard";
import VeillePage from "./pages/VeillePage";
import AODetailPage from "./pages/AODetailPage";
import KanbanPage from "./pages/KanbanPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import RedacteurPage from "./pages/RedacteurPage";
import SoumissionsPage from "./pages/SoumissionsPage";
import PricingPage from "./pages/PricingPage";
import SubscriptionPage from "./pages/SubscriptionPage";
import OnboardingPage from "./pages/OnboardingPage";
import StripeCheckout from "./components/StripeCheckout";

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
};

function AdminUsers() {
  return <div><h2>Admin - Users</h2></div>;
}

function AdminTenants() {
  return <div><h2>Admin - Tenants</h2></div>;
}

function DocumentsPage() {
  return (
    <div>
      <h2>Documents</h2>
      <DocumentUpload />
    </div>
  );
}

function MemoryPage() {
  return (
    <div>
      <h2>Memory</h2>
      <MemorySearch />
    </div>
  );
}

function HILPage() {
  return (
    <div>
      <h2>Human-in-the-Loop</h2>
      <HILDashboard />
    </div>
  );
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
          <Link to="/veille" style={{ color: "#fff", marginRight: "1rem" }}>Veille</Link>
          <Link to="/kanban" style={{ color: "#fff", marginRight: "1rem" }}>Kanban</Link>
          <Link to="/admin/dashboard" style={{ color: "#fff", marginRight: "1rem" }}>Admin</Link>
          <Link to="/admin/users" style={{ color: "#fff", marginRight: "1rem" }}>Users</Link>
          <Link to="/admin/tenants" style={{ color: "#fff", marginRight: "1rem" }}>Tenants</Link>
          <Link to="/documents" style={{ color: "#fff", marginRight: "1rem" }}>Documents</Link>
          <Link to="/memory" style={{ color: "#fff", marginRight: "1rem" }}>Memory</Link>
          <Link to="/hil" style={{ color: "#fff", marginRight: "1rem" }}>HIL</Link>
          <Link to="/pricing" style={{ color: "#fff", marginRight: "1rem" }}>Tarifs</Link>
          <button onClick={logout}>Logout</button>
        </>
      )}
    </nav>
  );
}

const App: FC = () => {
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
              <Route path="/veille" element={<VeillePage />} />
              <Route path="/ao/:aoId" element={<AODetailPage />} />
              <Route path="/kanban" element={<KanbanPage />} />
              <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
              <Route path="/admin/users" element={<AdminUsers />} />
              <Route path="/admin/tenants" element={<AdminTenants />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/memory" element={<MemoryPage />} />
              <Route path="/hil" element={<HILPage />} />
              <Route path="/redacteur" element={<RedacteurPage />} />
              <Route path="/soumissions" element={<SoumissionsPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/subscription" element={<SubscriptionPage />} />
              <Route path="/onboarding" element={<OnboardingPage />} />
              <Route path="/checkout" element={<StripeCheckout />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
