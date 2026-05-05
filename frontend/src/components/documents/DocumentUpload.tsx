// File: frontend/src/components/documents/DocumentUpload.tsx
// Purpose: Document upload component with parsing trigger

import { useState, FormEvent } from "react";
import { useAuth } from "../AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export default function DocumentUpload() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    setResult(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      const doc = await res.json();

      const parseRes = await fetch(`${API_BASE}/documents/${doc.id}/parse?target_level=4`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!parseRes.ok) throw new Error(await parseRes.text());
      const parseData = await parseRes.json();
      setResult(parseData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <h3>Upload Document</h3>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button type="submit" disabled={!file || uploading}>
          {uploading ? "Processing..." : "Upload & Parse"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && (
        <div style={{ marginTop: 16, background: "#f5f5f5", padding: 12 }}>
          <p><strong>Level reached:</strong> {result.level_reached}</p>
          <p><strong>Degraded:</strong> {result.degraded ? "Yes" : "No"}</p>
          <p><strong>Processing time:</strong> {result.processing_time_ms}ms</p>
          <pre style={{ fontSize: 12 }}>{JSON.stringify(result.entities, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
