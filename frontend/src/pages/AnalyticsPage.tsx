import { FC, useEffect, useState } from "react";
import { useAuth } from "../components/AuthContext";
import {
  BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area,
} from "recharts";

interface DashboardData {
  funnel: any;
  roi: any;
  sources: any[];
  predictions: any[];
  trends: any[];
}

const COLORS = ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#10b981"];

const AnalyticsPage: FC = () => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<"overview" | "funnel" | "roi" | "predictions">("overview");
  const [period, setPeriod] = useState(30);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    loadDashboard();
  }, [token, period]);

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/analytics/dashboard", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement analytics");
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p style={{ padding: "2rem" }}>Chargement...</p>;
  if (error) return <p style={{ color: "red", padding: "2rem" }}>{error}</p>;
  if (!data) return <p style={{ padding: "2rem" }}>Aucune donnee</p>;

  const tabs = [
    { id: "overview" as const, label: "Vue d'ensemble" },
    { id: "funnel" as const, label: "Funnel" },
    { id: "roi" as const, label: "ROI" },
    { id: "predictions" as const, label: "Predictions" },
  ];

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Analytics & Performance</h2>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        {[7, 30, 90, 365].map((d) => (
          <button
            key={d}
            onClick={() => setPeriod(d)}
            style={{
              padding: "0.4rem 0.8rem",
              border: "1px solid #ccc",
              background: period === d ? "#333" : "#fff",
              color: period === d ? "#fff" : "#333",
              borderRadius: "0.25rem",
              cursor: "pointer",
            }}
          >
            {d === 365 ? "1 an" : `${d}j`}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", borderBottom: "2px solid #eee" }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: "0.5rem 1rem",
              borderBottom: activeTab === t.id ? "2px solid #e94560" : "2px solid transparent",
              fontWeight: activeTab === t.id ? "bold" : "normal",
              background: "none",
              border: "none",
              cursor: "pointer",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && <OverviewTab data={data} />}
      {activeTab === "funnel" && <FunnelTab funnel={data.funnel} />}
      {activeTab === "roi" && <ROITab roi={data.roi} />}
      {activeTab === "predictions" && <PredictionsTab predictions={data.predictions} />}
    </div>
  );
};

const OverviewTab: FC<{ data: DashboardData }> = ({ data }) => {
  const funnel = data.funnel || {};
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        <KpiCard title="AO Detectes" value={funnel.total_detected || 0} color="#e3f2fd" />
        <KpiCard title="Scorés" value={funnel.total_scored || 0} color="#f3e5f5" />
        <KpiCard title="Qualifiés" value={funnel.total_qualified || 0} color="#e8f5e9" />
        <KpiCard title="Soumis" value={funnel.total_submitted || 0} color="#fff3e0" />
      </div>

      <div style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "1rem" }}>
        <h4>Evolution des AO</h4>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data.trends || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="detected" stroke="#0f3460" fill="#0f3460" fillOpacity={0.3} name="AO detectes" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <h4>Performance par source</h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data.sources || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="source_name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_detected" fill="#e94560" name="AO detectes" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const FunnelTab: FC<{ funnel: any }> = ({ funnel }) => {
  if (!funnel) return <p>Aucune donnee de funnel</p>;
  const chartData = [
    { name: "Detectes", value: funnel.total_detected || 0 },
    { name: "Scorés", value: funnel.total_scored || 0 },
    { name: "Qualifiés", value: funnel.total_qualified || 0 },
    { name: "Soumis", value: funnel.total_submitted || 0 },
    { name: "Confirmés", value: funnel.total_confirmed || 0 },
  ];

  return (
    <div>
      <div style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "1rem" }}>
        <h4>Funnel de conversion</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {funnel.conversion_rates && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem" }}>
          {Object.entries(funnel.conversion_rates).map(([key, value]: [string, any]) => (
            <div key={key} style={{ background: "#fff", padding: "0.75rem", borderRadius: "0.25rem", boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
              <p style={{ fontSize: "0.75rem", color: "#666", margin: 0 }}>{key.replace(/_/g, " ")}</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", margin: 0 }}>{value}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ROITab: FC<{ roi: any }> = ({ roi }) => {
  if (!roi) return <p>Aucune donnee ROI</p>;
  const positive = (roi.roi_percent || 0) > 0;

  return (
    <div>
      <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "0.5rem", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", marginBottom: "1rem" }}>
        <h4>ROI sur {roi.period_months} mois</h4>
        <p style={{ fontSize: "3rem", fontWeight: "bold", color: positive ? "#10b981" : "#ef4444", margin: "0.5rem 0" }}>
          {roi.roi_percent}%
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem", marginTop: "1rem" }}>
          <div style={{ background: "#f9fafb", padding: "0.75rem", borderRadius: "0.25rem" }}>
            <p style={{ fontSize: "0.75rem", color: "#666", margin: 0 }}>Gain estime</p>
            <p style={{ fontSize: "1.25rem", fontWeight: "bold", margin: 0 }}>{(roi.estimated_gain || 0).toLocaleString("fr-FR")} €</p>
          </div>
          <div style={{ background: "#f9fafb", padding: "0.75rem", borderRadius: "0.25rem" }}>
            <p style={{ fontSize: "0.75rem", color: "#666", margin: 0 }}>Cout abonnement</p>
            <p style={{ fontSize: "1.25rem", fontWeight: "bold", margin: 0 }}>{(roi.taka_subscription_cost || 0).toLocaleString("fr-FR")} €</p>
          </div>
          <div style={{ background: "#f9fafb", padding: "0.75rem", borderRadius: "0.25rem" }}>
            <p style={{ fontSize: "0.75rem", color: "#666", margin: 0 }}>Benefice net</p>
            <p style={{ fontSize: "1.25rem", fontWeight: "bold", margin: 0 }}>{(roi.net_benefit || 0).toLocaleString("fr-FR")} €</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const PredictionsTab: FC<{ predictions: any[] }> = ({ predictions }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
        <p>Aucune prediction disponible</p>
        <p style={{ fontSize: "0.85rem" }}>Les predictions apparaissent lorsque des AO sont scorés</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
      {predictions.map((pred) => (
        <div key={pred.ao_id} style={{ background: "#fff", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <span style={{ fontWeight: "bold" }}>AO #{pred.ao_id.slice(0, 8)}</span>
            <span style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{(pred.probability * 100).toFixed(0)}%</span>
          </div>
          <span style={{
            display: "inline-block",
            padding: "0.2rem 0.5rem",
            borderRadius: "1rem",
            fontSize: "0.75rem",
            fontWeight: "bold",
            background: pred.confidence === "high" ? "#d1fae5" : pred.confidence === "medium" ? "#fef3c7" : "#f3f4f6",
            color: pred.confidence === "high" ? "#065f46" : pred.confidence === "medium" ? "#92400e" : "#4b5563",
          }}>
            Confiance {pred.confidence}
          </span>
          {pred.explanation && <p style={{ fontSize: "0.85rem", color: "#555", marginTop: "0.5rem" }}>{pred.explanation}</p>}
        </div>
      ))}
    </div>
  );
};

const KpiCard: FC<{ title: string; value: number; color: string }> = ({ title, value, color }) => (
  <div style={{ background: color, padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
    <p style={{ fontSize: "0.8rem", color: "#555", margin: 0 }}>{title}</p>
    <p style={{ fontSize: "1.75rem", fontWeight: "bold", margin: "0.25rem 0 0" }}>{value}</p>
  </div>
);

export default AnalyticsPage;
