import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';

const TIERS = [
  {
    name: 'free',
    label: 'Free',
    price: '0',
    period: '',
    features: [
      '10 AO par mois',
      '1 ligne metier',
      '1 utilisateur',
      '100 Mo stockage',
      'Scoring de base',
    ],
    cta: 'Commencer gratuitement',
    highlighted: false,
  },
  {
    name: 'pro',
    label: 'Pro',
    price: '49',
    period: '/mois',
    features: [
      '100 AO par mois',
      '5 lignes metiers',
      '10 utilisateurs',
      '1 Go stockage',
      'Scoring avance',
      'Dashboard avance',
      'Support prioritaire',
    ],
    cta: 'Souscrire au plan Pro',
    highlighted: true,
  },
  {
    name: 'enterprise',
    label: 'Enterprise',
    price: '199',
    period: '/mois',
    features: [
      'AO illimites',
      'Lignes metiers illimitees',
      'Utilisateurs illimites',
      '10 Go stockage',
      'API access',
      'Personnalisation marque',
      'Support dedie',
    ],
    cta: 'Contacter les ventes',
    highlighted: false,
  },
];

export default function PricingPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [yearly, setYearly] = useState(false);

  const handleSelect = (tierName: string) => {
    if (!token) {
      navigate('/register');
      return;
    }
    if (tierName === 'free') {
      navigate('/onboarding');
      return;
    }
    navigate(`/subscription?tier=${tierName}&yearly=${yearly}`);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '72rem', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Choisissez votre plan
        </h1>
        <p style={{ color: '#6b7280' }}>Commencez gratuitement, evoluez selon vos besoins.</p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
        <button
          onClick={() => setYearly(false)}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem 0 0 0.375rem',
            border: '1px solid #d1d5db',
            background: yearly ? '#f3f4f6' : '#2563eb',
            color: yearly ? '#374151' : '#fff',
            cursor: 'pointer',
          }}
        >
          Mensuel
        </button>
        <button
          onClick={() => setYearly(true)}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '0 0.375rem 0.375rem 0',
            border: '1px solid #d1d5db',
            borderLeft: 'none',
            background: yearly ? '#2563eb' : '#f3f4f6',
            color: yearly ? '#fff' : '#374151',
            cursor: 'pointer',
          }}
        >
          Annuel (-17%)
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        {TIERS.map((tier) => (
          <div
            key={tier.name}
            style={{
              border: tier.highlighted ? '2px solid #2563eb' : '1px solid #e5e7eb',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              background: '#fff',
              position: 'relative',
            }}
          >
            {tier.highlighted && (
              <div
                style={{
                  position: 'absolute',
                  top: '-0.75rem',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: '#2563eb',
                  color: '#fff',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}
              >
                Populaire
              </div>
            )}
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              {tier.label}
            </h3>
            <div style={{ marginBottom: '1rem' }}>
              <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>
                {tier.price === '0' ? 'Gratuit' : `${tier.price} EUR`}
              </span>
              {tier.period && (
                <span style={{ color: '#6b7280' }}>{yearly ? '/an' : tier.period}</span>
              )}
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem 0' }}>
              {tier.features.map((f, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  <span style={{ color: '#16a34a', marginRight: '0.5rem' }}>&#10003;</span>
                  {f}
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleSelect(tier.name)}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: tier.highlighted ? '#2563eb' : '#f3f4f6',
                color: tier.highlighted ? '#fff' : '#374151',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {tier.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
