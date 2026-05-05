// File: frontend/src/components/hil/HILDashboard.tsx
// Purpose: Human-in-the-loop pending requests dashboard

import { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

interface HILRequest {
  id: number;
  scope: string;
  decision_type: string;
  context: Record<string, any>;
  status: string;
  expires_at: string | null;
  created_at: string;
}

export default function HILDashboard() {
  const { token } = useAuth();
  const [requests, setRequests] = useState<HILRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchPending = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/hil/pending`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      setRequests(await res.json());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, [token]);

  const resolve = async (id: number, decision: string, notes?: string) => {
    try {
      const res = await fetch(`${API_BASE}/hil/${id}/resolve`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ decision, notes }),
      });
      if (!res.ok) throw new Error(await res.text());
      await fetchPending();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <h3>HIL Pending Requests</h3>
      <button onClick={fetchPending} disabled={loading}>
        {loading ? "Loading..." : "Refresh"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {requests.length === 0 && <p>No pending requests.</p>}
      <ul style={{ marginTop: 16 }}>
        {requests.map((req) => (
          <li key={req.id} style={{ marginBottom: 16, border: "1px solid #ccc", padding: 12 }}>
            <p><strong>#{req.id}</strong> — {req.decision_type} ({req.scope})</p>
            <p style={{ fontSize: 12, color: "#666" }}>
              Created: {new Date(req.created_at).toLocaleString()}
            </p>
            {req.expires_at && (
              <p style={{ fontSize: 12, color: "#666" }}>
                Expires: {new Date(req.expires_at).toLocaleString()}
              </p>
            )}
            <pre style={{ fontSize: 11, background: "#f5f5f5", padding: 8 }}>
              {JSON.stringify(req.context, null, 2)}
            </pre>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => resolve(req.id, "approved")}>Approve</button>{" "}
              <button onClick={() => resolve(req.id, "rejected", "Rejected by user")}>Reject</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
