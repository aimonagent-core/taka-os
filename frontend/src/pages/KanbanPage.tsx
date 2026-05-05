import { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';

interface KanbanAO {
  id: string;
  title: string;
  estimated_amount: number | null;
  currency: string;
  deadline_date: string | null;
  department_code: string | null;
  score_global: number;
  business_line_color: string | null;
}

interface Column {
  id: string;
  title: string;
  color: string;
  borderColor: string;
  aos: KanbanAO[];
}

export default function KanbanPage() {
  const { token } = useAuth();
  const [columns, setColumns] = useState<Column[]>([
    { id: 'GO', title: 'GO — Postuler', color: '#f0fdf4', borderColor: '#bbf7d0', aos: [] },
    { id: 'MAYBE', title: 'MAYBE — A etudier', color: '#fefce8', borderColor: '#fde047', aos: [] },
    { id: 'NO_GO', title: 'NO-GO — Rejeter', color: '#fef2f2', borderColor: '#fecaca', aos: [] },
    { id: 'PENDING', title: 'En attente', color: '#f9fafb', borderColor: '#e5e7eb', aos: [] },
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKanbanData();
  }, []);

  const fetchKanbanData = async () => {
    try {
      const res = await fetch('/api/v1/veille/aos?status=scored&page_size=100', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      const aos = data.items || [];

      const newColumns: Column[] = columns.map((col) => ({ ...col, aos: [] as KanbanAO[] }));

      for (const ao of aos) {
        const verdict = ao.scoring_result?.verdict || 'PENDING';
        const col = newColumns.find((c) => c.id === verdict) || newColumns[3];
        col.aos.push({
          id: ao.id,
          title: ao.title,
          estimated_amount: ao.estimated_amount,
          currency: ao.currency,
          deadline_date: ao.deadline_date,
          department_code: ao.department_code,
          score_global: ao.scoring_result?.score_global || 0,
          business_line_color: ao.business_line?.color || null,
        });
      }

      for (const col of newColumns) {
        col.aos.sort((a, b) => b.score_global - a.score_global);
      }

      setColumns(newColumns);
    } catch (err) {
      console.error('Erreur Kanban:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (e: React.DragEvent, aoId: string, sourceColumn: string) => {
    e.dataTransfer.setData('aoId', aoId);
    e.dataTransfer.setData('sourceColumn', sourceColumn);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, targetColumn: string) => {
    e.preventDefault();
    const aoId = e.dataTransfer.getData('aoId');
    const sourceColumn = e.dataTransfer.getData('sourceColumn');

    if (!aoId || sourceColumn === targetColumn) return;

    const newColumns = columns.map((col) => {
      if (col.id === sourceColumn) {
        return { ...col, aos: col.aos.filter((a) => a.id !== aoId) };
      }
      if (col.id === targetColumn) {
        const ao = columns.find((c) => c.id === sourceColumn)?.aos.find((a) => a.id === aoId);
        if (ao) return { ...col, aos: [...col.aos, ao] };
      }
      return col;
    });
    setColumns(newColumns);
  };

  if (loading) {
    return (
      <div style={{ padding: '1.5rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Kanban Qualification</h1>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} style={{ height: '24rem', background: '#f3f4f6', borderRadius: '0.5rem' }} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Kanban Qualification</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        {columns.map((column) => (
          <div
            key={column.id}
            style={{
              borderRadius: '0.5rem',
              border: `2px solid ${column.borderColor}`,
              background: column.color,
              padding: '0.75rem',
              minHeight: '500px',
            }}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h2 style={{ fontWeight: 600, fontSize: '1rem', margin: 0 }}>{column.title}</h2>
              <span style={{
                padding: '0.125rem 0.5rem',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                background: '#e5e7eb',
              }}>
                {column.aos.length}
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {column.aos.map((ao) => (
                <div
                  key={ao.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, ao.id, column.id)}
                  style={{
                    background: '#fff',
                    borderRadius: '0.375rem',
                    padding: '0.75rem',
                    cursor: 'grab',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  }}
                >
                  <p style={{ fontSize: '0.875rem', fontWeight: 500, margin: '0 0 0.5rem 0', lineHeight: 1.4 }}>{ao.title}</p>
                  <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.75rem', color: '#6b7280', flexWrap: 'wrap' }}>
                    <span style={{ padding: '0.125rem 0.375rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}>
                      {ao.score_global.toFixed(1)}
                    </span>
                    {ao.estimated_amount && (
                      <span>{(ao.estimated_amount / 1000).toFixed(0)}k {ao.currency}</span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem', fontSize: '0.75rem', color: '#9ca3af' }}>
                    {ao.department_code && <span>&#128205; {ao.department_code}</span>}
                    {ao.deadline_date && <span>&#128197; {new Date(ao.deadline_date).toLocaleDateString('fr-FR')}</span>}
                  </div>
                  {ao.business_line_color && (
                    <div style={{ width: '100%', height: '0.25rem', borderRadius: '9999px', marginTop: '0.5rem', background: ao.business_line_color }} />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
