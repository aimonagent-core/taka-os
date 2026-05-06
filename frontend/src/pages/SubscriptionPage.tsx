import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';

interface SubscriptionData {
  tier_name: string;
  status: string;
  stripe_subscription_id: string | null;
  trial_ends_at: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
}

export default function SubscriptionPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { token } = useAuth();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);

  const tierParam = searchParams.get('tier');
  const yearlyParam = searchParams.get('yearly') === 'true';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchSubscription();
  }, [token]);

  const fetchSubscription = async () => {
    try {
      const res = await fetch('/api/v1/billing/subscription', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json();
      if (json.status === 'success') {
        setSubscription(json.data);
      }
    } catch (err) {
      console.error('Erreur chargement souscription:', err);
    } finally {
      setLoading(false);
    }
  };

  const startCheckout = async () => {
    if (!tierParam) return;
    try {
      const res = await fetch(
        `/api/v1/billing/checkout-session?tier_name=${tierParam}&yearly=${yearlyParam}`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const json = await res.json();
      if (json.status === 'success' && json.data.url) {
        window.location.href = json.data.url;
      } else {
        alert('Erreur lors de la creation de la session de paiement');
      }
    } catch (err) {
      console.error('Erreur checkout:', err);
      alert('Erreur lors de la creation de la session de paiement');
    }
  };

  const openPortal = async () => {
    setPortalLoading(true);
    try {
      const res = await fetch('/api/v1/billing/portal-session', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json();
      if (json.status === 'success' && json.data.url) {
        window.location.href = json.data.url;
      }
    } catch (err) {
      console.error('Erreur portal:', err);
    } finally {
      setPortalLoading(false);
    }
  };

  if (loading) return <div style={{ padding: '2rem' }}>Chargement...</div>;

  const tierLabels: Record<string, string> = {
    free: 'Free',
    pro: 'Pro',
    enterprise: 'Enterprise',
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '48rem', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>
        Ma souscription
      </h1>

      {subscription && (
        <div
          style={{
            background: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.75rem',
            padding: '1.5rem',
            marginBottom: '1.5rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>Plan actuel</p>
              <p style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: '0.25rem 0 0 0' }}>
                {tierLabels[subscription.tier_name] || subscription.tier_name}
              </p>
            </div>
            <div>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>Statut</p>
              <p
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  margin: '0.25rem 0 0 0',
                  color: subscription.status === 'active' ? '#16a34a' : '#dc2626',
                }}
              >
                {subscription.status}
              </p>
            </div>
          </div>

          {subscription.trial_ends_at && (
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1rem' }}>
              Periode d'essai jusqu'au {new Date(subscription.trial_ends_at).toLocaleDateString('fr-FR')}
            </p>
          )}

          {subscription.current_period_end && (
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1rem' }}>
              Prochaine periode jusqu'au {new Date(subscription.current_period_end).toLocaleDateString('fr-FR')}
            </p>
          )}

          {subscription.stripe_subscription_id && (
            <button
              onClick={openPortal}
              disabled={portalLoading}
              style={{
                padding: '0.75rem 1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid #d1d5db',
                background: '#fff',
                cursor: 'pointer',
                fontWeight: 500,
              }}
            >
              {portalLoading ? 'Chargement...' : 'Gerer ma souscription (Stripe)'}
            </button>
          )}
        </div>
      )}

      {tierParam && subscription?.tier_name === 'free' && (
        <div
          style={{
            background: '#eff6ff',
            border: '1px solid #bfdbfe',
            borderRadius: '0.75rem',
            padding: '1.5rem',
          }}
        >
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Passer au plan {tierLabels[tierParam]}
          </h2>
          <p style={{ color: '#374151', marginBottom: '1rem' }}>
            Vous allez etre redirige vers Stripe pour finaliser votre paiement en toute securite.
          </p>
          <button
            onClick={startCheckout}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              background: '#2563eb',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Payer maintenant
          </button>
        </div>
      )}
    </div>
  );
}
