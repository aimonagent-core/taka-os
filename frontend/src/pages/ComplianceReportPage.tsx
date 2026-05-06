import { FC, useEffect, useState } from "react";
import { useAuth } from "../components/AuthContext";

interface Report {
  id: string;
  report_type: string;
  title: string;
  status: string;
  pdf_url: string;
  pdf_size_bytes: number;
  summary_data: any;
  generated_at: string;
}

interface Anomaly {
  id: string;
  type: string;
  severity: string;
  status: string;
  title: string;
  description: string;
  ai_analysis: string;
  ai_recommendation: string;
  created_at: string;
}

const ComplianceReportPage: FC = () => {
  const { token } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedReportType, setSelectedReportType] = useState("submission_proof");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [reportTitle, setReportTitle] = useState("");
  const [activeTab, setActiveTab] = useState<"reports" | "anomalies">("reports");

  useEffect(() => {
    if (!token) return;
    loadReports();
    loadAnomalies();
  }, [token]);

  const loadReports = async () => {
    try {
      const res = await fetch("/api/v1/compliance/reports", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement rapports");
      const data = await res.json();
      setReports(data.items || []);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const loadAnomalies = async () => {
    try {
      const res = await fetch("/api/v1/compliance/anomalies", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement anomalies");
      const data = await res.json();
      setAnomalies(data.items || []);
    } catch (e: any) {
      // Silencieux — anomalies sont optionnelles
    }
  };

  const createReport = async () => {
    if (!token) return;
    if (!reportTitle) {
      setError("Titre requis");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        report_type: selectedReportType,
        title: reportTitle,
      });
      if (periodStart) params.set("period_start", new Date(periodStart).toISOString());
      if (periodEnd) params.set("period_end", new Date(periodEnd).toISOString());

      const res = await fetch(`/api/v1/compliance/reports?${params}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erreur creation rapport");
      }
      await loadReports();
      setReportTitle("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runAnomalyCheck = async (reportId: string) => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/compliance/reports/${reportId}/anomalies`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur execution checks");
      await loadAnomalies();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (reportId: string) => {
    window.open(`/api/v1/compliance/reports/${reportId}/download`, "_blank");
  };

  const resolveAnomaly = async (anomalyId: string) => {
    if (!token) return;
    const note = window.prompt("Note de resolution :") || "Resolu manuellement";
    try {
      const res = await fetch(`/api/v1/compliance/anomalies/${anomalyId}/resolve`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ resolution_note: note }),
      });
      if (!res.ok) throw new Error("Erreur resolution");
      await loadAnomalies();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const severityColor = (s: string) => {
    switch (s?.toLowerCase()) {
      case "critical": return "#dc2626";
      case "high": return "#ef4444";
      case "medium": return "#f59e0b";
      case "low": return "#3b82f6";
      default: return "#6b7280";
    }
  };

  return (
    <div>
      <h2>Conformite & Audit</h2>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <button onClick={() => setActiveTab("reports")} style={{ fontWeight: activeTab === "reports" ? "bold" : "normal" }}>
          Rapports
        </button>
        <button onClick={() => setActiveTab("anomalies")} style={{ fontWeight: activeTab === "anomalies" ? "bold" : "normal" }}>
          Anomalies ({anomalies.length})
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {activeTab === "reports" && (
        <>
          <div style={{ border: "1px solid #e5e7eb", padding: "1rem", marginBottom: "1rem", borderRadius: "0.5rem" }}>
            <h3>Nouveau rapport</h3>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.5rem" }}>
              <select value={selectedReportType} onChange={(e) => setSelectedReportType(e.target.value)}>
                <option value="submission_proof">Preuve de depot</option>
                <option value="monthly_compliance">Rapport mensuel</option>
              </select>
              <input
                placeholder="Titre du rapport"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                style={{ minWidth: 200 }}
              />
            </div>
            {selectedReportType === "monthly_compliance" && (
              <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <input type="date" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} />
                <input type="date" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} />
              </div>
            )}
            <button onClick={createReport} disabled={loading}>
              {loading ? "Generation..." : "Generer"}
            </button>
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f3f4f6" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Type</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Titre</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Statut</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Taille</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Genere le</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                  <td style={{ padding: "0.5rem" }}>{r.report_type}</td>
                  <td style={{ padding: "0.5rem" }}>{r.title}</td>
                  <td style={{ padding: "0.5rem" }}>{r.status}</td>
                  <td style={{ padding: "0.5rem" }}>
                    {r.pdf_size_bytes ? `${(r.pdf_size_bytes / 1024).toFixed(1)} Ko` : "—"}
                  </td>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem" }}>
                    {r.generated_at ? new Date(r.generated_at).toLocaleDateString("fr-FR") : "—"}
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <button onClick={() => downloadReport(r.id)} style={{ marginRight: "0.5rem" }}>
                      Telecharger
                    </button>
                    <button onClick={() => runAnomalyCheck(r.id)}>Verifier anomalies</button>
                  </td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr><td colSpan={6} style={{ padding: "1rem", textAlign: "center" }}>Aucun rapport</td></tr>
              )}
            </tbody>
          </table>
        </>
      )}

      {activeTab === "anomalies" && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f3f4f6" }}>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Date</th>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Type</th>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Titre</th>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Severite</th>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Statut</th>
              <th style={{ textAlign: "left", padding: "0.5rem" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.map((a) => (
              <tr key={a.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                <td style={{ padding: "0.5rem", fontSize: "0.85rem" }}>
                  {new Date(a.created_at).toLocaleString("fr-FR")}
                </td>
                <td style={{ padding: "0.5rem" }}>{a.type}</td>
                <td style={{ padding: "0.5rem" }}>{a.title}</td>
                <td style={{ padding: "0.5rem", color: severityColor(a.severity), fontWeight: "bold" }}>
                  {a.severity}
                </td>
                <td style={{ padding: "0.5rem" }}>{a.status}</td>
                <td style={{ padding: "0.5rem" }}>
                  {a.status !== "resolved" && (
                    <button onClick={() => resolveAnomaly(a.id)}>Resoudre</button>
                  )}
                </td>
              </tr>
            ))}
            {anomalies.length === 0 && (
              <tr><td colSpan={6} style={{ padding: "1rem", textAlign: "center" }}>Aucune anomalie detectee</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ComplianceReportPage;
