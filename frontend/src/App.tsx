// File: frontend/src/App.tsx
// Purpose: Root App component with ErrorBoundary, routes, auth context, and PWA

import { FC } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { Toaster } from "sonner";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { AuthProvider, useAuth } from "./components/AuthContext";
import { useAuthStore } from "./store/useAuthStore";
import { usePWA } from "./hooks/usePWA";
import NotificationBell from "./components/NotificationBell";
import DocumentUpload from "./components/documents/DocumentUpload";
import MemorySearch from "./components/memory/MemorySearch";
import HILDashboard from "./components/hil/HILDashboard";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import VeillePage from "./pages/VeillePage";
import AODetailPage from "./pages/AODetailPage";
import KanbanPage from "./pages/KanbanPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import DashboardPage from "./pages/DashboardPage";
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
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">TAKA OS</h1>
        <p className="text-lg text-gray-600 mb-8">
          Plateforme intelligente de veille et de matching d'appels d'offres pour les entreprises du BTP et des services.
        </p>
        {user ? (
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Accéder au Dashboard
          </Link>
        ) : (
          <div className="flex gap-4 justify-center">
            <Link
              to="/login"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              Se connecter
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-lg shadow-sm text-gray-700 bg-white hover:bg-gray-50"
            >
              S'inscrire
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

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
  const { isAuthenticated } = useAuthStore();
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
          📡 Mode hors ligne — certaines données peuvent être obsolètes
        </div>
      )}
      <nav style={{ padding: "1rem", background: "#333", color: "#fff" }}>
        <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <Link to="/" style={{ color: "#fff", marginRight: "1rem" }}>Home</Link>
          {!user && !isAuthenticated && (
            <>
              <Link to="/login" style={{ color: "#fff", marginRight: "1rem" }}>Login</Link>
              <Link to="/register" style={{ color: "#fff", marginRight: "1rem" }}>Register</Link>
              <Link to="/onboarding" style={{ color: "#fff", marginRight: "1rem" }}>Onboarding</Link>
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
              <Link to="/compliance" style={{ color: "#fff", marginRight: "1rem" }}>Conformité</Link>
              <Link to="/analytics" style={{ color: "#fff", marginRight: "1rem" }}>Analytics</Link>
              <Link to="/collaboration" style={{ color: "#fff", marginRight: "1rem" }}>Collaboration</Link>
              <Link to="/pricing" style={{ color: "#fff", marginRight: "1rem" }}>Tarifs</Link>
              <button
                onClick={logout}
                className="px-3 py-1.5 rounded text-sm font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
              >
                Logout
              </button>
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <NotificationBell />
              </div>
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
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
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
      <Toaster position="top-right" richColors closeButton duration={5000} />
    </ErrorBoundary>
  );
};

export default App;
