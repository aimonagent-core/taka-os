import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuth } from '../components/AuthContext';
import { useAuthStore } from '../store/useAuthStore';

interface LoginResponse {
  status: string;
  data: {
    access_token?: string;
    refresh_token?: string;
    token_type?: string;
    mfa_required?: boolean;
    mfa_token?: string;
  };
  message?: string;
}

interface MeResponse {
  status: string;
  data: {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    tenant_id: string;
  };
}

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { setAuth } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [showMfa, setShowMfa] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, mfa_code: mfaCode || undefined }),
      });

      const json: LoginResponse = await res.json();

      if (!res.ok) {
        toast.error(json.message || 'Identifiants invalides');
        setLoading(false);
        return;
      }

      // MFA requis
      if (json.data?.mfa_required) {
        setMfaToken(json.data.mfa_token || '');
        setShowMfa(true);
        setMfaCode('');
        toast.info('Code MFA requis');
        setLoading(false);
        return;
      }

      const accessToken = json.data?.access_token;
      if (!accessToken) {
        toast.error('Token manquant dans la réponse');
        setLoading(false);
        return;
      }

      await finalizeAuth(accessToken);
    } catch {
      toast.error('Erreur réseau. Vérifiez votre connexion.');
    } finally {
      setLoading(false);
    }
  };

  const handleMfaVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/v1/auth/mfa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mfa_token: mfaToken, code: mfaCode }),
      });

      const json: LoginResponse = await res.json();

      if (!res.ok) {
        toast.error(json.message || 'Code MFA invalide');
        setLoading(false);
        return;
      }

      const accessToken = json.data?.access_token;
      if (!accessToken) {
        toast.error('Token manquant');
        setLoading(false);
        return;
      }

      await finalizeAuth(accessToken);
    } catch {
      toast.error('Erreur réseau.');
    } finally {
      setLoading(false);
    }
  };

  const finalizeAuth = async (accessToken: string) => {
    try {
      const meRes = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!meRes.ok) {
        toast.error('Impossible de récupérer le profil utilisateur');
        return;
      }

      const meJson: MeResponse = await meRes.json();
      const user = meJson.data;

      login(accessToken, user);
      setAuth(
        {
          id: Number(user.id),
          email: user.email,
          first_name: user.full_name?.split(' ')[0] || null,
          last_name: user.full_name?.split(' ').slice(1).join(' ') || null,
          role: user.role,
        },
        accessToken
      );

      toast.success('Connexion réussie !');
      navigate('/dashboard');
    } catch {
      toast.error('Erreur lors de la finalisation de la connexion');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-sm border border-gray-200">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">TAKA OS</h1>
          <p className="mt-2 text-sm text-gray-500">
            {showMfa ? 'Vérification MFA' : 'Connectez-vous à votre compte'}
          </p>
        </div>

        {!showMfa ? (
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Adresse email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="vous@entreprise.fr"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                'Se connecter'
              )}
            </button>

            <div className="text-center text-sm">
              <span className="text-gray-500">Pas encore de compte ?</span>{' '}
              <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
                S'inscrire
              </Link>
            </div>
          </form>
        ) : (
          <form onSubmit={handleMfaVerify} className="space-y-5">
            <div>
              <label htmlFor="mfa" className="block text-sm font-medium text-gray-700 mb-1">
                Code MFA
              </label>
              <input
                id="mfa"
                type="text"
                inputMode="numeric"
                required
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="123456"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                'Vérifier'
              )}
            </button>

            <button
              type="button"
              onClick={() => { setShowMfa(false); setMfaCode(''); setMfaToken(''); }}
              className="w-full text-center text-sm text-gray-500 hover:text-gray-700"
            >
              Retour à la connexion
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
