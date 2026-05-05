import { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';

interface AOToWrite {
  id: string;
  title: string;
  verdict: string;
  score_global: number;
  business_line_name: string | null;
}

interface GeneratedResponse {
  id: string;
  category: string;
  content: string;
  status: string;
  hil_status: string;
  generation_time_ms: number;
  created_at: string;
}

export default function RedacteurPage() {
  const { token } = useAuth();
  const [aos, setAos] = useState<AOToWrite[]>([]);
  const [selectedAO, setSelectedAO] = useState<string | null>(null);
  const [category, setCategory] = useState("letter");
  const [customPrompt, setCustomPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [response, setResponse] = useState<GeneratedResponse | null>(null);
  const [responses, setResponses] = useState<GeneratedResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { fetchAOsToWrite(); fetchResponses(); }, []);

  const fetchAOsToWrite = async () => {
    try {
      const res = await fetch('/api/v1/veille/aos?verdict=GO&page_size=50', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      const items = (data.items || []).filter((ao: any) =>
        ao.scoring_result?.verdict === 'GO' || ao.scoring_result?.verdict === 'MAYBE'
      );
      setAos(items.map((ao: any) => ({
        id: ao.id,
        title: ao.title,
        verdict: ao.scoring_result?.verdict,
        score_global: ao.scoring_result?.score_global,
        business_line_name: ao.business_line?.name,
      })));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchResponses = async () => {
    try {
      const res = await fetch('/api/v1/redacteur/responses', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setResponses(data);
      }
    } catch (err) {
      console.error('Erreur chargement réponses:', err);
    }
  };

  const handleGenerate = async () => {
    if (!selectedAO) return;
    setGenerating(true);
    setError("");
    try {
      const params = new URLSearchParams({ category });
      if (customPrompt) params.append('custom_prompt', customPrompt);
      const res = await fetch(`/api/v1/redacteur/generate/${selectedAO}?${params}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        setResponse(data);
        setResponses([data, ...responses]);
      } else {
        setError(data.detail || 'Erreur de génération');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async (responseId: string) => {
    try {
      const res = await fetch(`/api/v1/redacteur/responses/${responseId}/approve`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setResponses(responses.map(r => r.id === responseId ? { ...r, status: 'approved', hil_status: 'validated' } : r));
        if (response && response.id === responseId) {
          setResponse({ ...response, status: 'approved', hil_status: 'validated' });
        }
      }
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  const handleReject = async (responseId: string) => {
    try {
      const res = await fetch(`/api/v1/redacteur/responses/${responseId}/reject`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setResponses(responses.map(r => r.id === responseId ? { ...r, status: 'rejected', hil_status: 'rejected' } : r));
        if (response && response.id === responseId) {
          setResponse({ ...response, status: 'rejected', hil_status: 'rejected' });
        }
      }
    } catch (err) {
      console.error('Erreur:', err);
    }
  };

  return (
    <div style={{ padding: '1.5rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Rédacteur — Génération de réponses</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        {/* Colonne AO */}
        <div>
          <div style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
            <h2 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>AO à rédiger (GO / MAYBE)</h2>
            {loading ? (
              <div>Chargement...</div>
            ) : (
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {aos.map((ao) => (
                  <div
                    key={ao.id}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      marginBottom: '0.5rem',
                      background: selectedAO === ao.id ? '#eff6ff' : '#f9fafb',
                      border: selectedAO === ao.id ? '1px solid #bfdbfe' : '1px solid transparent',
                    }}
                    onClick={() => setSelectedAO(ao.id)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <p style={{ fontSize: '0.875rem', fontWeight: 500 }}>{ao.title}</p>
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '0.125rem 0.5rem',
                        borderRadius: '9999px',
                        background: ao.verdict === 'GO' ? '#dcfce7' : '#fef9c3',
                        color: ao.verdict === 'GO' ? '#166534' : '#854d0e',
                      }}>{ao.verdict}</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                      Score: {ao.score_global}
                      {ao.business_line_name && <span> • {ao.business_line_name}</span>}
                    </div>
                  </div>
                ))}
                {aos.length === 0 && <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Aucun AO qualifié</p>}
              </div>
            )}
          </div>
        </div>

        {/* Colonne Génération */}
        <div>
          {selectedAO ? (
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
              <h2 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Générer une réponse</h2>
              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Catégorie</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                >
                  <option value="letter">Lettre de candidature</option>
                  <option value="technical">Dossier technique</option>
                  <option value="financial">Offre financière</option>
                  <option value="administrative">Pièces administratives</option>
                </select>
              </div>
              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Instructions additionnelles (optionnel)</label>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  rows={3}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                />
              </div>
              {error && <div style={{ color: '#dc2626', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{error}</div>}
              <button
                onClick={handleGenerate}
                disabled={generating}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: generating ? '#9ca3af' : '#2563eb',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '0.375rem',
                  cursor: generating ? 'not-allowed' : 'pointer',
                }}
              >
                {generating ? 'Génération en cours...' : 'Générer'}
              </button>

              {response && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <button onClick={() => handleApprove(response.id)} style={{ padding: '0.5rem 1rem', background: '#16a34a', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}>
                      Approuver
                    </button>
                    <button onClick={() => handleReject(response.id)} style={{ padding: '0.5rem 1rem', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}>
                      Rejeter
                    </button>
                  </div>
                  <div style={{ background: '#f9fafb', padding: '1rem', borderRadius: '0.375rem', maxHeight: '300px', overflowY: 'auto', whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                    {response.content}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
              Sélectionnez un AO dans la liste pour générer une réponse
            </div>
          )}

          {responses.length > 0 && (
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', marginTop: '1.5rem' }}>
              <h2 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Réponses générées récemment</h2>
              <div>
                {responses.map((r) => (
                  <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem', marginBottom: '0.5rem' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', padding: '0.125rem 0.5rem', borderRadius: '9999px', border: '1px solid #d1d5db', textTransform: 'capitalize' }}>{r.category}</span>
                      <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#6b7280' }}>{r.generation_time_ms}ms</span>
                    </div>
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '0.125rem 0.5rem',
                      borderRadius: '9999px',
                      background: r.status === 'approved' ? '#dcfce7' : r.status === 'rejected' ? '#fee2e2' : '#dbeafe',
                      color: r.status === 'approved' ? '#166534' : r.status === 'rejected' ? '#991b1b' : '#1e40af',
                    }}>{r.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
