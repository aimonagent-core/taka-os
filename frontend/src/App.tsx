// File: frontend/src/App.tsx
// Purpose: Root App component with ErrorBoundary, routes, auth context, and PWA

import { FC } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { AuthProvider, useAuth } from "./components/AuthContext";
import { useAuthStore } from "./store/useAuthStore";
import { usePWA } from "./hooks/usePWA";
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
import AuditTrailPage from "./pages/AuditTrailPage";
import ComplianceReportPage from "./pages/ComplianceReportPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import CollaborationPage from "./pages/CollaborationPage";
import NotFoundPage from "./pages/NotFoundPage";
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
  const { isAuthenticated, token } = useAuthStore();
  const { isInstallable, isInstalled, isOnline, install } = usePWA();

  return (
    <>
      {!isOnline && (
        <div
          style={{
            background: "#f59e0b",
            color: "#fff",
            textAlign: "center",
            padding: "0.5rem 1rem",
            fontSize: "0.875rem",
          }}
        >
          📡 Mode hors ligne — certaines donnees peuvent etre obsoletes
        </div>
      )}
      <nav style={{ padding: "1rem", background: "#333", color: "#fff" }}>
        <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <Link to="/" style={{ color: "#fff", marginRight: "1rem" }}>Home</Link>
          {!user && (
            <>
              <Link to="/login" style={{ color: "#fff", marginRight: "1rem" }}>Login</Link>
              <Link to="/register" style={{ color: "#fff", marginRight: "1rem" }}>Register</Link>
            </>
          )}
          {user && isAuthenticated && (
            <>
              <Link to="/dashboard" style={{ color: "#fff", marginRight: "1rem" }}>Dashboard</Link>
              <Link to="/veille" style={{ color: "#fff", marginRight: "1rem" }}>Veille</Link>
              <Link to="/kanban" style={{ color: "#fff", marginRight: "1rem" }}>Kanban</Link>
              <Link to="/admin/dashboard" style={{ color: "#fff", marginRight: "1rem" }}>Admin</Link>
              <Link to="/documents" style={{ color: "#fff", marginRight: "1rem" }}>Documents</Link>
              <Link to="/memory" style={{ color: "#fff", marginRight: "1rem" }}>Memory</Link>
              <Link to="/hil" style={{ color: "#fff", marginRight: "1rem" }}>HIL</Link>
              <Link to="/audit" style={{ color: "#fff", marginRight: "1rem" }}>Audit</Link>
              <Link to="/compliance" style={{ color: "#fff", marginRight: "1rem" }}>Conformite</Link>
              <Link to="/analytics" style={{ color: "#fff", marginRight: "1rem" }}>Analytics</Link>
              <Link to="/collaboration" style={{ color: "#fff", marginRight: "1rem" }}>Collaboration</Link>
              <Link to="/pricing" style={{ color: "#fff", marginRight: "1rem" }}>Tarifs</Link>
              <button onClick={logout}>Logout</button>
            </>
          )}
          {isInstallable && !isInstalled && (
            <button
              onClick={install}
              style={{
                marginLeft: "auto",
                padding: "0.4rem 0.8rem",
                background: "#10b981",
                color: "#fff",
                border: "none",
                borderRadius: "0.25rem",
                cursor: "pointer",
                fontSize: "0.875rem",
              }}
            >
              📲 Installer TAKA OS
            </button>
          )}
        </div>
      </nav>
    </>
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
              <Route path="/audit" element={<AuditTrailPage />} />
              <Route path="/compliance" element={<ComplianceReportPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/collaboration" element={<CollaborationPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/subscription" element={<SubscriptionPage />} />
              <Route path="/onboarding" element={<OnboardingPage />} />
              <Route path="/checkout" element={<StripeCheckout />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
