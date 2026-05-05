import { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';

interface Submission {
  id: string;
  response_id: string;
  platform_name: string;
  platform_type: string;
  status: string;
  platform_reference: string | null;
  retry_count: number;
  submitted_at: string | null;
  created_at: string;
}

interface Platform {
  id: string;
  name: string;
  platform_type: string;
  is_mock: boolean;
}

export default function SoumissionsPage() {
  const { token } = useAuth();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [subRes, platRes] = await Promise.all([
        fetch('/api/v1/deposant/submissions', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/deposant/platforms', { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      const subData = await subRes.json();
      const platData = await platRes.json();
      setSubmissions(subData);
      setPlatforms(platData);
    } catch (err) {
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrack = async () => {
    try {
      const res = await fetch('/api/v1/deposant/track', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error('Erreur track:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'submitted': return { bg: '#dbeafe', text: '#1e40af' };
      case 'confirmed': return { bg: '#dcfce7', text: '#166534' };
      case 'rejected': return { bg: '#fee2e2', text: '#991b1b' };
      case 'pending': return { bg: '#fef9c3', text: '#854d0e' };
      default: return { bg: '#f3f4f6', text: '#374151' };
    }
  };

  return (
    <div style={{ padding: '1.5rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Suivi des dépôts</h1>
        <button
          onClick={handleTrack}
          style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', background: '#fff', cursor: 'pointer' }}
        >
          Vérifier les statuts
        </button>
      </div>

      {/* Plateformes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {platforms.map((p) => (
          <div key={p.id} style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ fontWeight: 600 }}>{p.name}</p>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', textTransform: 'capitalize' }}>{p.platform_type}</p>
              </div>
              <span style={{
                fontSize: '0.75rem',
                padding: '0.125rem 0.5rem',
                borderRadius: '9999px',
                background: p.is_mock ? '#f3f4f6' : '#dbeafe',
                color: '#374151',
              }}>{p.is_mock ? 'Mock' : 'Live'}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Soumissions */}
      <div style={{ border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
        <h2 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Historique des soumissions</h2>
        {loading ? (
          <div>Chargement...</div>
        ) : (
          <div>
            {submissions.map((s) => {
              const colors = getStatusColor(s.status);
              return (
                <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem', marginBottom: '0.5rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '0.125rem 0.5rem',
                        borderRadius: '9999px',
                        background: colors.bg,
                        color: colors.text,
                      }}>{s.status}</span>
                      <span style={{ fontWeight: 500 }}>{s.platform_name || s.platform_type}</span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' }}>
                      {s.platform_reference && <span>Ref: {s.platform_reference}</span>}
                      {s.retry_count > 0 && <span style={{ marginLeft: '0.5rem' }}>Retries: {s.retry_count}</span>}
                      {s.submitted_at && <span style={{ marginLeft: '0.5rem' }}>Soumis: {new Date(s.submitted_at).toLocaleDateString('fr-FR')}</span>}
                    </div>
                  </div>
                  <div>
                    {s.status === 'rejected' && s.retry_count < 3 && (
                      <button style={{ padding: '0.25rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', background: '#fff', fontSize: '0.875rem', cursor: 'pointer' }}>
                        Relancer
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            {submissions.length === 0 && (
              <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>Aucune soumission enregistrée</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
