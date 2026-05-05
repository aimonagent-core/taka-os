import { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';

interface KPIsData {
  total_ao_detected: number;
  ao_qualified_go: number;
  ao_rejected_nogo: number;
  ao_pending_maybe: number;
  qualification_rate_pct: number;
  total_amount_qualified_eur: number;
  avg_response_delay_days: number;
  top_source: { name: string | null; count: number };
  avg_global_score: number;
  ao_by_country: { country: string; count: number }[];
  evolution_daily: { date: string; count: number }[];
}

export default function AdminDashboardPage() {
  const { token } = useAuth();
  const [kpis, setKpis] = useState<KPIsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [periodDays, setPeriodDays] = useState(30);

  useEffect(() => {
    fetchKPIs();
  }, [periodDays]);

  const fetchKPIs = async () => {
    try {
      const res = await fetch(`/api/v1/dashboard/kpis?period_days=${periodDays}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setKpis(data);
    } catch (err) {
      console.error('Erreur KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div style={{ margin: '1.5rem', height: '100vh', background: '#f3f4f6', borderRadius: '0.5rem' }} />;
  if (!kpis) return <div style={{ padding: '1.5rem' }}>Erreur de chargement</div>;

  return (
    <div style={{ padding: '1.5rem', maxWidth: '80rem', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Dashboard Administrateur</h1>
        <select
          value={periodDays}
          onChange={(e) => setPeriodDays(Number(e.target.value))}
          style={{ padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
        >
          <option value={7}>7 jours</option>
          <option value={30}>30 jours</option>
          <option value={90}>90 jours</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>AO Detectes</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.25rem 0 0 0' }}>{kpis.total_ao_detected}</p>
            </div>
            <span style={{ fontSize: '1.5rem' }}>&#128065;</span>
          </div>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>Qualifies (GO)</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.25rem 0 0 0', color: '#16a34a' }}>{kpis.ao_qualified_go}</p>
            </div>
            <span style={{ fontSize: '1.5rem' }}>&#128200;</span>
          </div>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>Taux de qualification</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.25rem 0 0 0' }}>{kpis.qualification_rate_pct}%</p>
            </div>
            <span style={{ fontSize: '1.5rem' }}>&#128202;</span>
          </div>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>Montant total GO</p>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0.25rem 0 0 0', color: '#16a34a' }}>
                {(kpis.total_amount_qualified_eur / 1000000).toFixed(1)}M &euro;
              </p>
            </div>
            <span style={{ fontSize: '1.5rem' }}>&#128176;</span>
          </div>
        </div>
      </div>

      {/* Graphiques */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Evolution temporelle */}
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Evolution journaliere</h3>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.25rem', height: '200px', paddingBottom: '1.5rem', position: 'relative' }}>
            {kpis.evolution_daily.length === 0 && <p style={{ color: '#9ca3af' }}>Aucune donnee</p>}
            {kpis.evolution_daily.map((day, i) => {
              const maxCount = Math.max(...kpis.evolution_daily.map(d => d.count), 1);
              const height = (day.count / maxCount) * 160;
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ height: `${height}px`, background: '#3b82f6', borderRadius: '0.125rem 0.125rem 0 0', width: '100%' }} />
                  <span style={{ fontSize: '0.625rem', color: '#6b7280', transform: 'rotate(-45deg)', whiteSpace: 'nowrap', position: 'absolute', bottom: 0 }}>
                    {new Date(day.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Repartition par pays */}
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Repartition par pays</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {kpis.ao_by_country.length === 0 && <p style={{ color: '#9ca3af' }}>Aucune donnee</p>}
            {kpis.ao_by_country.map((item, i) => {
              const total = kpis.ao_by_country.reduce((sum, c) => sum + c.count, 0);
              const pct = total > 0 ? (item.count / total) * 100 : 0;
              const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
              return (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                    <span>{item.country}</span>
                    <span>{item.count} ({pct.toFixed(0)}%)</span>
                  </div>
                  <div style={{ height: '0.5rem', background: '#e5e7eb', borderRadius: '9999px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: colors[i % colors.length], borderRadius: '9999px' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Deuxieme rangee */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Source principale</h3>
          <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#2563eb', margin: 0 }}>{kpis.top_source.name || 'N/A'}</p>
          <p style={{ color: '#6b7280', marginTop: '0.25rem' }}>{kpis.top_source.count} AO sur la periode</p>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Delai moyen de reponse</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>&#9201;</span>
            <span style={{ fontSize: '1.875rem', fontWeight: 'bold' }}>{kpis.avg_response_delay_days}</span>
            <span style={{ color: '#6b7280' }}>jours</span>
          </div>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Score moyen global</h3>
          <p style={{
            fontSize: '1.875rem',
            fontWeight: 'bold',
            margin: 0,
            color: kpis.avg_global_score >= 7 ? '#16a34a' : kpis.avg_global_score >= 4 ? '#ca8a04' : '#dc2626',
          }}>
            {kpis.avg_global_score.toFixed(1)}
          </p>
          <p style={{ color: '#6b7280', marginTop: '0.25rem' }}>/ 10</p>
        </div>
      </div>
    </div>
  );
}
