import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function StripeCheckout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { token } = useAuth();

  const sessionId = searchParams.get('session_id');
  const tier = searchParams.get('tier');
  const yearly = searchParams.get('yearly') === 'true';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    if (sessionId) {
      // Redirection apres paiement Stripe — on redirige vers la page souscription
      navigate('/subscription');
      return;
    }

    if (tier) {
      // Demarrer le checkout
      startCheckout();
    }
  }, [token, sessionId, tier]);

  const startCheckout = async () => {
    try {
      const res = await fetch(
        `/api/v1/billing/checkout-session?tier_name=${tier}&yearly=${yearly}`,
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
        navigate('/pricing');
      }
    } catch (err) {
      console.error('Erreur checkout:', err);
      alert('Erreur lors de la creation de la session de paiement');
      navigate('/pricing');
    }
  };

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <p>Redirection vers Stripe...</p>
    </div>
  );
}
