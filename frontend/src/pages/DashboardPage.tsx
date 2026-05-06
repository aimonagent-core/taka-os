import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { toast } from 'sonner';

// =============================================================================
// Types
// =============================================================================

interface DashboardStats {
  ao_this_week: number;
  ao_this_week_delta: number | null;
  imminent_deadlines: number;
  match_rate_pct: number;
  new_since_last_login: number;
  ao_by_type: { label: string; value: number; color?: string }[];
  weekly_evolution: { label: string; value: number }[];
}

interface AOItem {
  id: string;
  title: string;
  buyer_name: string | null;
  deadline_date: string | null;
  days_until_deadline: number | null;
  deadline_badge: 'urgent' | 'soon' | 'normal' | 'none';
  match_score: number;
  ao_type: string | null;
  url: string | null;
  is_new: boolean;
}

interface SearchResult {
  id: string;
  title: string;
  buyer_name: string | null;
  deadline_date: string | null;
  notice_type: string | null;
}

// =============================================================================
// Constantes
// =============================================================================

const TYPE_COLORS: Record<string, string> = {
  Travaux: '#3b82f6',
  Services: '#22c55e',
  Fournitures: '#6b7280',
  Concession: '#a855f7',
};

const BADGE_STYLES: Record<string, string> = {
  urgent: 'bg-red-100 text-red-700 border-red-200',
  soon: 'bg-orange-100 text-orange-700 border-orange-200',
  normal: 'bg-green-100 text-green-700 border-green-200',
  none: 'bg-gray-100 text-gray-600 border-gray-200',
};

// =============================================================================
// Composant principal
// =============================================================================

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAO, setRecentAO] = useState<AOItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);

  const token = localStorage.getItem('token') || '';

  const apiFetch = useCallback(
    async (url: string) => {
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    [token]
  );

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [statsData, aoData] = await Promise.all([
          apiFetch('/api/v1/dashboard/stats'),
          apiFetch('/api/v1/dashboard/recent-ao?limit=5'),
        ]);
        if (!cancelled) {
          setStats(statsData);
          setRecentAO(aoData.items || []);
        }
      } catch {
        if (!cancelled) toast.error('Impossible de charger le dashboard');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [apiFetch]);

  // Recherche debounce
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }
    const t = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const data = await apiFetch(`/api/v1/veille/ao/search?q=${encodeURIComponent(searchQuery)}&limit=8`);
        setSearchResults(data.items || []);
        setShowSearchDropdown(true);
      } catch {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [searchQuery, apiFetch]);

  const handleSearchSelect = (id: string) => {
    setSearchQuery('');
    setShowSearchDropdown(false);
    navigate(`/ao/${id}`);
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header + recherche */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500">Vue d'ensemble de vos appels d'offres</p>
          </div>

          <div className="relative w-full sm:w-80">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => { if (searchResults.length) setShowSearchDropdown(true); }}
              placeholder="Rechercher un AO..."
              className="w-full px-4 py-2 pl-10 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {searchLoading && (
              <svg className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            )}

            {showSearchDropdown && searchResults.length > 0 && (
              <ul className="absolute z-20 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-64 overflow-auto">
                {searchResults.map((r) => (
                  <li
                    key={r.id}
                    onClick={() => handleSearchSelect(r.id)}
                    className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0"
                  >
                    <div className="text-sm font-medium text-gray-900 truncate">{r.title}</div>
                    <div className="text-xs text-gray-500">{r.buyer_name || r.notice_type || 'AO'}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label="AO cette semaine"
            value={stats?.ao_this_week ?? 0}
            delta={stats?.ao_this_week_delta}
            deltaLabel="vs sem. derniere"
            icon="📊"
          />
          <KpiCard
            label="Deadlines imminentes"
            value={stats?.imminent_deadlines ?? 0}
            alert={!!stats && stats.imminent_deadlines > 0}
            icon="⏰"
          />
          <KpiCard
            label="Taux de match"
            value={`${Math.round(stats?.match_rate_pct ?? 0)}%`}
            icon="🎯"
          />
          <KpiCard
            label="Nouveautes"
            value={stats?.new_since_last_login ?? 0}
            icon="✨"
          />
        </div>

        {/* Graphique + Liste */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Graphique */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Repartition par type de marche</h3>
            {stats && stats.ao_by_type.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.ao_by_type}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {stats.ao_by_type.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color || '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState message="Aucune donnee disponible pour le graphique" />
            )}
          </div>

          {/* Evolution hebdo mini */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Evolution 7 jours</h3>
            {stats && stats.weekly_evolution.some((d) => d.value > 0) ? (
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.weekly_evolution}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState message="Pas assez de donnees" />
            )}
          </div>
        </div>

        {/* Liste AO pertinents */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-700">AO les plus pertinents</h3>
            <button
              onClick={() => navigate('/veille')}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Voir tout →
            </button>
          </div>

          {recentAO.length === 0 ? (
            <EmptyState message="Aucun AO trouve pour votre profil. Verifiez vos preferences CPV." />
          ) : (
            <div className="divide-y divide-gray-100">
              {recentAO.map((ao) => (
                <div
                  key={ao.id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-gray-50 transition-colors px-2 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {ao.is_new && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          Nouveau
                        </span>
                      )}
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {ao.title.length > 80 ? `${ao.title.slice(0, 80)}...` : ao.title}
                      </h4>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {ao.buyer_name || 'Acheteur non specifie'}
                      {ao.ao_type && (
                        <span
                          className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border"
                          style={{
                            backgroundColor: `${TYPE_COLORS[ao.ao_type] || '#6b7280'}15`,
                            color: TYPE_COLORS[ao.ao_type] || '#6b7280',
                            borderColor: `${TYPE_COLORS[ao.ao_type] || '#6b7280'}30`,
                          }}
                        >
                          {ao.ao_type}
                        </span>
                      )}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    {ao.days_until_deadline !== null && (
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${BADGE_STYLES[ao.deadline_badge] || BADGE_STYLES.none}`}>
                        {ao.days_until_deadline === 0
                          ? "Aujourd'hui"
                          : `Dans ${ao.days_until_deadline}j`}
                      </span>
                    )}

                    <div className="flex items-center gap-1">
                      <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${ao.match_score}%`,
                            backgroundColor:
                              ao.match_score >= 70
                                ? '#22c55e'
                                : ao.match_score >= 40
                                ? '#f59e0b'
                                : '#6b7280',
                          }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-600 w-8 text-right">
                        {Math.round(ao.match_score)}%
                      </span>
                    </div>

                    <button
                      onClick={() => navigate(`/ao/${ao.id}`)}
                      className="text-xs text-blue-600 hover:text-blue-700 font-medium whitespace-nowrap"
                    >
                      Voir detail
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sous-composants
// =============================================================================

function KpiCard({
  label,
  value,
  delta,
  deltaLabel,
  alert,
  icon,
}: {
  label: string;
  value: string | number;
  delta?: number | null;
  deltaLabel?: string;
  alert?: boolean;
  icon: string;
}) {
  const deltaPositive = delta !== null && delta !== undefined && delta >= 0;
  const deltaNegative = delta !== null && delta !== undefined && delta < 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 relative overflow-hidden">
      {alert && (
        <span className="absolute top-3 right-3 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
        </span>
      )}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{icon}</span>
        <span className="text-sm font-medium text-gray-500">{label}</span>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
      {(deltaPositive || deltaNegative) && (
        <div className={`text-xs font-medium mt-1 flex items-center gap-1 ${deltaPositive ? 'text-green-600' : 'text-red-600'}`}>
          <span>{deltaPositive ? '↑' : '↓'}</span>
          <span>{Math.abs(delta!).toFixed(1)}%</span>
          {deltaLabel && <span className="text-gray-400 font-normal">{deltaLabel}</span>}
        </div>
      )}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <svg className="h-12 w-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}

// =============================================================================
// Skeleton loading
// =============================================================================

function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8 animate-pulse">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 h-28" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6 h-80" />
          <div className="bg-white rounded-xl border border-gray-200 p-6 h-80" />
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 h-64" />
      </div>
    </div>
  );
}
