import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';

interface AO {
  id: string;
  title: string;
  status: string;
  country: string;
  estimated_amount: number | null;
  currency: string;
  deadline_date: string | null;
  department_code: string | null;
  buyer_name: string | null;
  scoring_result: {
    verdict: string;
    score_global: number;
  } | null;
  business_line_id: string | null;
  created_at: string;
}

export default function VeillePage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [aos, setAos] = useState<AO[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    country: '',
    verdict: '',
    search: '',
    page: 1,
    page_size: 20,
  });
  const [pagination, setPagination] = useState({ total: 0, total_pages: 0 });

  const fetchAOs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.country) params.append('country', filters.country);
      if (filters.verdict) params.append('verdict', filters.verdict);
      if (filters.search) params.append('search', filters.search);
      params.append('page', String(filters.page));
      params.append('page_size', String(filters.page_size));

      const res = await fetch(`/api/v1/veille/aos?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setAos(data.items || []);
      setPagination(data.pagination || { total: 0, total_pages: 0 });
    } catch (err) {
      console.error('Erreur chargement AO:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAOs();
  }, [filters.page, filters.status, filters.country, filters.verdict]);

  const getVerdictColor = (verdict: string | null) => {
    switch (verdict) {
      case 'GO': return { background: '#dcfce7', color: '#166534' };
      case 'NO_GO': return { background: '#fee2e2', color: '#991b1b' };
      case 'MAYBE': return { background: '#fef9c3', color: '#854d0e' };
      default: return { background: '#f3f4f6', color: '#374151' };
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      detected: 'Detecte',
      parsing: 'Analyse en cours',
      parsed: 'Analyse',
      scoring: 'Scoring...',
      scored: 'Score',
      qualified: 'Qualifie',
      rejected: 'Rejete',
      error: 'Erreur',
    };
    return labels[status] || status;
  };

  return (
    <div style={{ padding: '1.5rem', maxWidth: '80rem', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Veille Appels d'Offres</h1>
        <button onClick={fetchAOs} style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', background: '#fff', cursor: 'pointer' }}>
          Actualiser
        </button>
      </div>

      {/* Filtres */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <input
            type="text"
            placeholder="Rechercher un AO..."
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            onKeyDown={(e) => e.key === 'Enter' && fetchAOs()}
          />
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          >
            <option value="">Tous les statuts</option>
            <option value="detected">Detecte</option>
            <option value="scored">Score</option>
            <option value="qualified">Qualifie</option>
            <option value="rejected">Rejete</option>
          </select>
          <select
            value={filters.country}
            onChange={(e) => setFilters({ ...filters, country: e.target.value, page: 1 })}
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          >
            <option value="">Tous les pays</option>
            <option value="FR">France</option>
            <option value="BE">Belgique</option>
            <option value="MA">Maroc</option>
            <option value="EU">Union Europeenne</option>
          </select>
          <select
            value={filters.verdict}
            onChange={(e) => setFilters({ ...filters, verdict: e.target.value, page: 1 })}
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          >
            <option value="">Tous les verdicts</option>
            <option value="GO">GO</option>
            <option value="NO_GO">NO-GO</option>
            <option value="MAYBE">MAYBE</option>
          </select>
        </div>
      </div>

      {/* Liste */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ height: '5rem', background: '#f3f4f6', borderRadius: '0.5rem', animation: 'pulse 2s infinite' }} />
          ))}
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {aos.map((ao) => (
              <div
                key={ao.id}
                onClick={() => navigate(`/ao/${ao.id}`)}
                style={{
                  background: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  cursor: 'pointer',
                  transition: 'box-shadow 0.2s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)')}
                onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontWeight: 600, fontSize: '1.125rem', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '600px' }}>
                        {ao.title}
                      </h3>
                      {ao.scoring_result && (
                        <span style={{ padding: '0.125rem 0.5rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600, ...getVerdictColor(ao.scoring_result.verdict) }}>
                          {ao.scoring_result.verdict} ({ao.scoring_result.score_global.toFixed(1)})
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#6b7280', flexWrap: 'wrap' }}>
                      <span>{getStatusLabel(ao.status)}</span>
                      <span>{ao.country}</span>
                      {ao.department_code && <span>Dept {ao.department_code}</span>}
                      {ao.estimated_amount && (
                        <span style={{ fontWeight: 500 }}>
                          {ao.estimated_amount.toLocaleString('fr-FR')} {ao.currency}
                        </span>
                      )}
                      {ao.deadline_date && (
                        <span style={{ color: '#ea580c' }}>
                          Limite: {new Date(ao.deadline_date).toLocaleDateString('fr-FR')}
                        </span>
                      )}
                      {ao.buyer_name && <span>{ao.buyer_name}</span>}
                    </div>
                  </div>
                  <span style={{ color: '#9ca3af', fontSize: '1.25rem' }}>&#10132;</span>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button
                disabled={filters.page <= 1}
                onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', background: '#fff', cursor: filters.page <= 1 ? 'not-allowed' : 'pointer', opacity: filters.page <= 1 ? 0.5 : 1 }}
              >
                Precedent
              </button>
              <span style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                Page {filters.page} / {pagination.total_pages}
              </span>
              <button
                disabled={filters.page >= pagination.total_pages}
                onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', background: '#fff', cursor: filters.page >= pagination.total_pages ? 'not-allowed' : 'pointer', opacity: filters.page >= pagination.total_pages ? 0.5 : 1 }}
              >
                Suivant
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
