import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';

type Step = 'register' | 'plan' | 'business_line' | 'complete';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [step, setStep] = useState<Step>('register');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Register fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [companyName, setCompanyName] = useState('');

  // Plan
  const [selectedPlan, setSelectedPlan] = useState('free');

  // Business line
  const [blName, setBlName] = useState('');
  const [cpvKeywords, setCpvKeywords] = useState('');

  const handleRegister = async () => {
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('email', email);
      formData.append('password', password);
      formData.append('full_name', fullName);
      formData.append('company_name', companyName);

      const res = await fetch('/api/v1/onboarding/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      const json = await res.json();
      if (json.status === 'success') {
        login(json.data.access_token, {
          id: json.data.user.id,
          email: json.data.user.email,
          full_name: json.data.user.full_name,
          role: 'admin',
          tenant_id: json.data.user.tenant_id,
        });
        setStep('plan');
      } else {
        setError(json.detail || json.message || 'Erreur lors de l\'inscription');
      }
    } catch (err) {
      setError('Erreur reseau');
    } finally {
      setLoading(false);
    }
  };

  const handlePlanSelect = (plan: string) => {
    setSelectedPlan(plan);
    if (plan === 'free') {
      setStep('business_line');
    } else {
      setStep('business_line');
    }
  };

  const handleSetup = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      const formData = new URLSearchParams();
      formData.append('business_line_name', blName);
      if (cpvKeywords) {
        cpvKeywords.split(',').forEach((k) => formData.append('cpv_keywords', k.trim()));
      }
      formData.append('plan_name', selectedPlan);

      const res = await fetch('/api/v1/onboarding/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      const json = await res.json();
      if (json.status === 'success') {
        setStep('complete');
      } else {
        setError(json.detail || json.message || 'Erreur lors de la configuration');
      }
    } catch (err) {
      setError('Erreur reseau');
    } finally {
      setLoading(false);
    }
  };

  const goToPayment = () => {
    navigate(`/subscription?tier=${selectedPlan}&yearly=false`);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '32rem', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', textAlign: 'center' }}>
        Bienvenue sur TAKA OS
      </h1>

      {/* Progress */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
        {(['register', 'plan', 'business_line', 'complete'] as Step[]).map((s, i) => (
          <div key={s} style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                width: '2rem',
                height: '2rem',
                borderRadius: '50%',
                background: step === s || (step === 'complete' && i < 3) ? '#2563eb' : '#e5e7eb',
                color: step === s || (step === 'complete' && i < 3) ? '#fff' : '#374151',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              {i + 1}
            </div>
            {i < 3 && (
              <div
                style={{
                  width: '2rem',
                  height: '2px',
                  background: step === 'complete' || (step === 'business_line' && i < 2) || (step === 'plan' && i < 1) ? '#2563eb' : '#e5e7eb',
                }}
              />
            )}
          </div>
        ))}
      </div>

      {error && (
        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            color: '#dc2626',
            padding: '0.75rem',
            borderRadius: '0.5rem',
            marginBottom: '1rem',
          }}
        >
          {error}
        </div>
      )}

      {step === 'register' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input
            type="text"
            placeholder="Nom complet"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <input
            type="text"
            placeholder="Nom de l'entreprise"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <button
            onClick={handleRegister}
            disabled={loading}
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              border: 'none',
              background: '#2563eb',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {loading ? 'Chargement...' : 'Creer mon compte'}
          </button>
        </div>
      )}

      {step === 'plan' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, textAlign: 'center' }}>
            Choisissez votre plan
          </h2>
          {['free', 'pro', 'enterprise'].map((plan) => (
            <button
              key={plan}
              onClick={() => handlePlanSelect(plan)}
              style={{
                padding: '1rem',
                borderRadius: '0.5rem',
                border: selectedPlan === plan ? '2px solid #2563eb' : '1px solid #e5e7eb',
                background: '#fff',
                textAlign: 'left',
                cursor: 'pointer',
              }}
            >
              <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{plan}</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                {plan === 'free' ? 'Gratuit' : plan === 'pro' ? '49 EUR/mois' : '199 EUR/mois'}
              </div>
            </button>
          ))}
        </div>
      )}

      {step === 'business_line' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, textAlign: 'center' }}>
            Configurez votre premiere ligne metier
          </h2>
          <input
            type="text"
            placeholder="Nom de la ligne metier (ex: BTP, IT, etc.)"
            value={blName}
            onChange={(e) => setBlName(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <input
            type="text"
            placeholder="Mots-cles CPV (separes par des virgules)"
            value={cpvKeywords}
            onChange={(e) => setCpvKeywords(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
          />
          <button
            onClick={handleSetup}
            disabled={loading}
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              border: 'none',
              background: '#2563eb',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {loading ? 'Chargement...' : 'Terminer la configuration'}
          </button>
        </div>
      )}

      {step === 'complete' && (
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#16a34a', marginBottom: '1rem' }}>
            &#10003; Configuration terminee !
          </h2>
          <p style={{ color: '#374151', marginBottom: '1.5rem' }}>
            Votre compte est pret. Commencez a explorer les appels d'offres.
          </p>
          {selectedPlan !== 'free' ? (
            <button
              onClick={goToPayment}
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
              Payer mon abonnement
            </button>
          ) : (
            <button
              onClick={() => navigate('/veille')}
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
              Acceder a la veille
            </button>
          )}
        </div>
      )}
    </div>
  );
}
