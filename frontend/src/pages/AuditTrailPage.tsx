import { FC, useEffect, useState } from "react";
import { useAuth } from "../components/AuthContext";

interface AuditLog {
  id: string;
  actor_type: string;
  actor_email: string;
  action: string;
  action_category: string;
  target_type: string;
  target_display: string;
  change_summary: string;
  severity: string;
  created_at: string;
}

const AuditTrailPage: FC = () => {
  const { token } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    action_category: "",
    severity: "",
    action: "",
  });

  const limit = 50;

  useEffect(() => {
    if (!token) return;
    loadLogs();
  }, [token, offset, filters]);

  const loadLogs = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(offset),
      });
      if (filters.action_category) params.set("action_category", filters.action_category);
      if (filters.severity) params.set("severity", filters.severity);
      if (filters.action) params.set("action", filters.action);

      const res = await fetch(`/api/v1/audit/logs?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Erreur chargement logs");
      const data = await res.json();
      setLogs(data.items || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = async () => {
    if (!token) return;
    const res = await fetch("/api/v1/audit/export/csv", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit_export_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const severityColor = (s: string) => {
    switch (s?.toLowerCase()) {
      case "critical": return "#dc2626";
      case "error": return "#ef4444";
      case "warning": return "#f59e0b";
      case "info": return "#3b82f6";
      default: return "#6b7280";
    }
  };

  return (
    <div>
      <h2>Journal d'Audit</h2>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        <input
          placeholder="Categorie"
          value={filters.action_category}
          onChange={(e) => { setOffset(0); setFilters({ ...filters, action_category: e.target.value }); }}
        />
        <input
          placeholder="Severite"
          value={filters.severity}
          onChange={(e) => { setOffset(0); setFilters({ ...filters, severity: e.target.value }); }}
        />
        <input
          placeholder="Action"
          value={filters.action}
          onChange={(e) => { setOffset(0); setFilters({ ...filters, action: e.target.value }); }}
        />
        <button onClick={exportCSV}>Exporter CSV</button>
      </div>

      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && logs.length === 0 && (
        <div style={{ textAlign: "center", padding: "3rem 1rem", color: "#6b7280" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📋</div>
          <h3 style={{ margin: "0 0 0.5rem" }}>Aucun evenement enregistre</h3>
          <p style={{ margin: 0 }}>L'audit trail enregistre automatiquement les actions importantes de votre organisation.</p>
        </div>
      )}

      {!loading && logs.length > 0 && (
        <>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f3f4f6" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Date</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Acteur</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Action</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Cible</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Resume</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Severite</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem" }}>
                    {new Date(log.created_at).toLocaleString("fr-FR")}
                  </td>
                  <td style={{ padding: "0.5rem" }}>{log.actor_email || log.actor_type}</td>
                  <td style={{ padding: "0.5rem" }}>{log.action}</td>
                  <td style={{ padding: "0.5rem" }}>
                    {log.target_type} — {log.target_display || log.target_type}
                  </td>
                  <td style={{ padding: "0.5rem", maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {log.change_summary}
                  </td>
                  <td style={{ padding: "0.5rem", color: severityColor(log.severity), fontWeight: "bold" }}>
                    {log.severity}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem", justifyContent: "center" }}>
            <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>Precedent</button>
            <span>Page {Math.floor(offset / limit) + 1} / {Math.ceil(total / limit) || 1}</span>
            <button disabled={offset + limit >= total} onClick={() => setOffset(offset + limit)}>Suivant</button>
          </div>
        </>
      )}
    </div>
  );
};

export default AuditTrailPage;
