import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuth } from '../components/AuthContext';

interface ScoringRun {
  id: string;
  profile: string;
  score_global: number;
  scores: {
    coherence: number;
    financiere: number;
    geographique: number;
    temporelle: number;
    concurrentielle: number;
  };
  verdict: string;
  confidence: number;
  recommendations: string[];
  details: Record<string, { score: number; explanation: string }>;
  created_at: string;
}

interface AODetail {
  id: string;
  title: string;
  description: string | null;
  status: string;
  country: string;
  estimated_amount: number | null;
  currency: string;
  deadline_date: string | null;
  department_code: string | null;
  buyer_name: string | null;
  contact_email: string | null;
  scoring_runs: ScoringRun[];
  business_line: { name: string; color: string } | null;
}

export default function AODetailPage() {
  const { aoId } = useParams<{ aoId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [ao, setAo] = useState<AODetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedProfile, setSelectedProfile] = useState<string>('prudent');
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    fetchAO();
  }, [aoId]);

  const fetchAO = async () => {
    try {
      const res = await fetch(`/api/v1/veille/aos/${aoId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setAo(data);
    } catch (err) {
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScore = async (profile: string) => {
    try {
      const res = await fetch(`/api/v1/scoring/run/${aoId}?profile=${profile}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        fetchAO();
        setSelectedProfile(profile);
      }
    } catch (err) {
      console.error('Erreur scoring:', err);
    }
  };

  const handleSimulateDeposit = async () => {
    setSimulating(true);
    try {
      // 1. Générer une réponse
      const genRes = await fetch(`/api/v1/redacteur/generate/${aoId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!genRes.ok) {
        const err = await genRes.json();
        toast.error(err.detail || 'Impossible de générer la réponse');
        setSimulating(false);
        return;
      }
      const generated = await genRes.json();
      const responseId = generated.data?.id || generated.id;
      if (!responseId) {
        toast.error('ID de réponse manquant');
        setSimulating(false);
        return;
      }

      // 2. Lister les plateformes
      const platRes = await fetch('/api/v1/deposant/platforms', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!platRes.ok) {
        toast.error('Impossible de récupérer les plateformes');
        setSimulating(false);
        return;
      }
      const platData = await platRes.json();
      const platforms = platData.platforms || [];
      if (platforms.length === 0) {
        toast.warning('Aucune plateforme de dépôt configurée');
        setSimulating(false);
        return;
      }
      // Privilégier la première plateforme mock ou la première disponible
      const platform = platforms.find((p: any) => p.is_mock) || platforms[0];

      // 3. Soumettre
      const subRes = await fetch(`/api/v1/deposant/submit/${responseId}/${platform.id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const subData = await subRes.json();
      if (!subRes.ok) {
        toast.error(subData.detail || 'Échec de la simulation de dépôt');
        setSimulating(false);
        return;
      }

      if (subData.is_mock || subData.data?.is_mock) {
        toast.success('Simulation de dépôt réussie (mode mock)');
      } else {
        toast.success('Dépôt soumis avec succès');
      }
    } catch {
      toast.error('Erreur lors de la simulation de dépôt');
    } finally {
      setSimulating(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'GO': return '#22c55e';
      case 'NO_GO': return '#ef4444';
      case 'MAYBE': return '#eab308';
      default: return '#6b7280';
    }
  };

  if (loading) return <div style={{ margin: '1.5rem', height: '24rem', background: '#f3f4f6', borderRadius: '0.5rem' }} />;
  if (!ao) return <div style={{ padding: '1.5rem' }}>AO non trouve</div>;

  const activeRun = ao.scoring_runs.find((r) => r.profile === selectedProfile) || ao.scoring_runs[0];

  return (
    <div style={{ padding: '1.5rem', maxWidth: '72rem', margin: '0 auto' }}>
      <button onClick={() => navigate('/veille')} style={{ marginBottom: '1rem', padding: '0.5rem', background: 'none', border: 'none', cursor: 'pointer', color: '#3b82f6' }}>
        &#8592; Retour
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {/* Colonne infos */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>{ao.title}</h2>
              {ao.business_line && (
                <span style={{ padding: '0.25rem 0.5rem', borderRadius: '9999px', fontSize: '0.75rem', color: '#fff', background: ao.business_line.color }}>
                  {ao.business_line.name}
                </span>
              )}
            </div>
            {ao.description && <p style={{ color: '#4b5563', marginBottom: '1rem' }}>{ao.description}</p>}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
              {ao.estimated_amount && (
                <div>
                  <span style={{ color: '#6b7280' }}>Montant estime:</span>
                  <p style={{ fontWeight: 600, margin: 0 }}>{ao.estimated_amount.toLocaleString('fr-FR')} {ao.currency}</p>
                </div>
              )}
              {ao.deadline_date && (
                <div>
                  <span style={{ color: '#6b7280' }}>Date limite:</span>
                  <p style={{ fontWeight: 600, margin: 0, color: '#ea580c' }}>{new Date(ao.deadline_date).toLocaleDateString('fr-FR')}</p>
                </div>
              )}
              {ao.department_code && (
                <div>
                  <span style={{ color: '#6b7280' }}>Departement:</span>
                  <p style={{ margin: 0 }}>{ao.department_code}</p>
                </div>
              )}
              <div>
                <span style={{ color: '#6b7280' }}>Pays:</span>
                <p style={{ margin: 0 }}>{ao.country}</p>
              </div>
              {ao.buyer_name && (
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: '#6b7280' }}>Acheteur:</span>
                  <p style={{ margin: 0 }}>{ao.buyer_name}</p>
                </div>
              )}
            </div>
          </div>

          {/* Actions scoring */}
          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Lancer le Scoring</h3>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['prudent', 'opportuniste', 'specialise'].map((p) => (
                <button
                  key={p}
                  onClick={() => handleScore(p)}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '0.375rem',
                    border: '1px solid #d1d5db',
                    background: selectedProfile === p ? '#3b82f6' : '#fff',
                    color: selectedProfile === p ? '#fff' : '#374151',
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Simuler dépôt */}
          <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Dépôt</h3>
            <button
              onClick={handleSimulateDeposit}
              disabled={simulating}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid #10b981',
                background: '#10b981',
                color: '#fff',
                cursor: simulating ? 'not-allowed' : 'pointer',
                opacity: simulating ? 0.6 : 1,
                fontWeight: 500,
              }}
            >
              {simulating ? 'Simulation en cours...' : 'Simuler dépôt'}
            </button>
          </div>

          {/* Recommandations */}
          {activeRun?.recommendations && activeRun.recommendations.length > 0 && (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
              <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Recommandations</h3>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {activeRun.recommendations.map((rec, i) => (
                  <li key={i} style={{ fontSize: '0.875rem', color: '#374151' }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Colonne scores */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {activeRun ? (
            <>
              {/* Verdict */}
              <div style={{ borderRadius: '0.5rem', padding: '1.5rem', textAlign: 'center', color: '#fff', background: getVerdictColor(activeRun.verdict) }}>
                <div style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>{activeRun.verdict}</div>
                <div style={{ fontSize: '1.125rem' }}>Score: {activeRun.score_global.toFixed(1)}/10</div>
                <div style={{ fontSize: '0.875rem', opacity: 0.8, marginTop: '0.25rem' }}>
                  Profil: {activeRun.profile} | Confiance: {(activeRun.confidence * 100).toFixed(0)}%
                </div>
              </div>

              {/* Radar chart simplifie - barres */}
              <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Dimensions de scoring</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {[
                    { label: 'Coherence', score: activeRun.scores.coherence },
                    { label: 'Financiere', score: activeRun.scores.financiere },
                    { label: 'Geographique', score: activeRun.scores.geographique },
                    { label: 'Temporelle', score: activeRun.scores.temporelle },
                    { label: 'Concurrentielle', score: activeRun.scores.concurrentielle },
                  ].map((dim) => (
                    <div key={dim.label}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                        <span>{dim.label}</span>
                        <span>{dim.score.toFixed(1)}/10</span>
                      </div>
                      <div style={{ height: '0.5rem', background: '#e5e7eb', borderRadius: '9999px', overflow: 'hidden' }}>
                        <div style={{ width: `${dim.score * 10}%`, height: '100%', background: '#3b82f6', borderRadius: '9999px' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Details par dimension */}
              <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Details</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(activeRun.details).map(([dim, info]) => (
                    <div key={dim} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                      <span style={{ textTransform: 'capitalize' }}>{dim}</span>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{
                          padding: '0.125rem 0.5rem',
                          borderRadius: '0.375rem',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: info.score >= 7 ? '#dcfce7' : info.score >= 4 ? '#f3f4f6' : '#fee2e2',
                          color: info.score >= 7 ? '#166534' : info.score >= 4 ? '#374151' : '#991b1b',
                        }}>
                          {info.score}/10
                        </span>
                        <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: '0.25rem 0 0 0', maxWidth: '200px' }}>{info.explanation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
              Aucun score disponible. Lancez le scoring pour voir les resultats.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
