// File: frontend/src/components/memory/MemorySearch.tsx
// Purpose: Memory search component

import { useState, FormEvent } from "react";
import { useAuth } from "../AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

interface MemoryResult {
  id: number;
  entry_type: string | null;
  content: string;
  layer: string;
  relevance_score: number | null;
  created_at: string | null;
}

export default function MemorySearch() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MemoryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${API_BASE}/memory/search?q=${encodeURIComponent(query)}&limit=10`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error(await res.text());
      setResults(await res.json());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 700 }}>
      <h3>Memory Search</h3>
      <form onSubmit={handleSearch}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search memory..."
          style={{ width: 300 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ul style={{ marginTop: 16 }}>
        {results.map((r) => (
          <li key={r.id} style={{ marginBottom: 12, borderBottom: "1px solid #ddd", paddingBottom: 8 }}>
            <span style={{ fontSize: 12, color: "#666" }}>[{r.layer}]</span>{" "}
            <span style={{ fontSize: 12, color: "#666" }}>{r.entry_type}</span>
            <p style={{ margin: "4px 0" }}>{r.content}</p>
            {r.relevance_score !== null && (
              <span style={{ fontSize: 12 }}>Score: {r.relevance_score.toFixed(3)}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
