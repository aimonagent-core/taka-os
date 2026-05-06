import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import { useAuthStore } from '../store/useAuthStore';
import { toast } from 'sonner';

// =============================================================================
// Types
// =============================================================================

type OnboardingStep = 1 | 2 | 3 | 4 | 5;

interface CPVItem {
  id: string;
  cpv_code: string;
  label: string;
}

interface OnboardingFormData {
  tenant_name: string;
  siret: string;
  admin_email: string;
  admin_password: string;
  admin_full_name: string;
  domaine_activite: string[];
  cpv_preferences: CPVItem[];
  effectif: string;
  ca_annuel: string;
  zones_geo: string[];
  types_marche_acceptes: string[];
  plan: string;
}

// =============================================================================
// Constantes
// =============================================================================

const DOMAINES = [
  'BTP',
  'Travaux publics',
  'Électricité',
  'Plomberie',
  'Menuiserie',
  'Maçonnerie',
  'Peinture',
  'Étanchéité',
  'Autre',
];

const EFFECTIFS = ['1-10', '11-50', '51-200', '201-500', '500+'];

const TYPES_MARCHE = ['Travaux', 'Services', 'Fournitures', 'Concession'];

// Departements 01-95 + DOM-TOM simplifie
const DEPARTEMENTS = Array.from({ length: 95 }, (_, i) =>
  String(i + 1).padStart(2, '0')
).concat(['971', '972', '973', '974', '976']);

const INITIAL_DATA: OnboardingFormData = {
  tenant_name: '',
  siret: '',
  admin_email: '',
  admin_password: '',
  admin_full_name: '',
  domaine_activite: [],
  cpv_preferences: [],
  effectif: '',
  ca_annuel: '',
  zones_geo: [],
  types_marche_acceptes: [],
  plan: 'free',
};

// =============================================================================
// Composant principal
// =============================================================================

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { setAuth } = useAuthStore();

  const [step, setStep] = useState<OnboardingStep>(1);
  const [form, setForm] = useState<OnboardingFormData>(INITIAL_DATA);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof OnboardingFormData, string>>>({});

  // CPV autocomplete
  const [cpvQuery, setCpvQuery] = useState('');
  const [cpvResults, setCpvResults] = useState<CPVItem[]>([]);
  const [cpvLoading, setCpvLoading] = useState(false);
  const cpvAbortRef = useRef<AbortController | null>(null);

  // ---------------------------------------------------------------------------
  // Helpers formulaire
  // ---------------------------------------------------------------------------

  const updateField = <K extends keyof OnboardingFormData>(
    key: K,
    value: OnboardingFormData[K]
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const toggleArrayItem = (key: 'domaine_activite' | 'zones_geo' | 'types_marche_acceptes', item: string) => {
    setForm((prev) => {
      const arr = prev[key];
      const exists = arr.includes(item);
      return { ...prev, [key]: exists ? arr.filter((i) => i !== item) : [...arr, item] };
    });
  };

  const addCPV = (item: CPVItem) => {
    if (form.cpv_preferences.length >= 10) {
      toast.error('Vous pouvez selectionner au maximum 10 CPV.');
      return;
    }
    if (form.cpv_preferences.some((c) => c.cpv_code === item.cpv_code)) return;
    setForm((prev) => ({ ...prev, cpv_preferences: [...prev.cpv_preferences, item] }));
    setCpvQuery('');
    setCpvResults([]);
  };

  const removeCPV = (code: string) => {
    setForm((prev) => ({
      ...prev,
      cpv_preferences: prev.cpv_preferences.filter((c) => c.cpv_code !== code),
    }));
  };

  // ---------------------------------------------------------------------------
  // Validation
  // ---------------------------------------------------------------------------

  const validateStep = (s: OnboardingStep): boolean => {
    const newErrors: Partial<Record<keyof OnboardingFormData, string>> = {};

    if (s === 1) {
      if (!form.tenant_name.trim()) newErrors.tenant_name = 'Nom de entreprise requis';
      if (!/^\d{14}$/.test(form.siret)) newErrors.siret = 'SIRET invalide (14 chiffres)';
      if (!form.admin_email.trim()) newErrors.admin_email = 'Email requis';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.admin_email))
        newErrors.admin_email = 'Email invalide';
      if (form.admin_password.length < 8)
        newErrors.admin_password = 'Mot de passe : 8 caracteres minimum';
    }

    if (s === 2) {
      if (form.domaine_activite.length === 0)
        newErrors.domaine_activite = 'Selectionnez au moins un domaine';
    }

    if (s === 3) {
      if (form.cpv_preferences.length === 0)
        newErrors.cpv_preferences = 'Selectionnez au moins un CPV';
    }

    if (s === 4) {
      if (!form.effectif) newErrors.effectif = 'Effectif requis';
      if (!form.ca_annuel || Number(form.ca_annuel) < 0)
        newErrors.ca_annuel = 'CA annuel requis';
      if (form.zones_geo.length === 0) newErrors.zones_geo = 'Selectionnez au moins un departement';
      if (form.types_marche_acceptes.length === 0)
        newErrors.types_marche_acceptes = 'Selectionnez au moins un type de marche';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const goNext = () => {
    if (!validateStep(step)) return;
    if (step < 5) setStep((s) => (s + 1) as OnboardingStep);
  };

  const goBack = () => {
    if (step > 1) setStep((s) => (s - 1) as OnboardingStep);
  };

  // ---------------------------------------------------------------------------
  // Autocomplete CPV
  // ---------------------------------------------------------------------------

  const fetchCPV = useCallback(async (q: string) => {
    if (q.length < 2) {
      setCpvResults([]);
      return;
    }
    setCpvLoading(true);
    if (cpvAbortRef.current) cpvAbortRef.current.abort();
    const ctrl = new AbortController();
    cpvAbortRef.current = ctrl;

    try {
      const res = await fetch(`/api/v1/blcpv-keywords/search?search=${encodeURIComponent(q)}&limit=10`, {
        signal: ctrl.signal,
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      });
      if (!res.ok) throw new Error('Erreur API');
      const data = await res.json();
      setCpvResults(data.items || []);
    } catch {
      setCpvResults([]);
    } finally {
      setCpvLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => fetchCPV(cpvQuery), 300);
    return () => clearTimeout(t);
  }, [cpvQuery, fetchCPV]);

  // ---------------------------------------------------------------------------
  // Soumission finale
  // ---------------------------------------------------------------------------

  const handleSubmit = async () => {
    if (!validateStep(step)) return;
    setLoading(true);

    try {
      const payload = {
        tenant_name: form.tenant_name,
        siret: form.siret,
        admin_email: form.admin_email,
        admin_password: form.admin_password,
        admin_full_name: form.admin_full_name || undefined,
        domaine_activite: form.domaine_activite,
        cpv_preferences: form.cpv_preferences.map((c) => ({
          cpv_code: c.cpv_code,
          label: c.label,
          weight: 1.0,
        })),
        effectif: form.effectif,
        ca_annuel: Number(form.ca_annuel),
        zones_geo: form.zones_geo,
        types_marche_acceptes: form.types_marche_acceptes,
        plan: form.plan,
      };

      const res = await fetch('/api/v1/onboarding/enterprise-setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || 'Erreur lors de la creation du compte');
        return;
      }

      // Authentifier l'utilisateur
      const user = {
        id: data.admin_user_id,
        email: data.admin_email,
        full_name: form.admin_full_name || form.admin_email,
        role: 'tenant_admin',
        tenant_id: data.tenant_id,
      };
      login(data.access_token, user);
      setAuth(user as any, data.access_token);

      toast.success('Onboarding termine ! Bienvenue sur TAKA OS.');
      navigate('/dashboard');
    } catch {
      toast.error('Une erreur est survenue. Reessayez.');
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------

  const stepLabels = ['Identite', 'Domaine', 'CPV', 'Contexte', 'Recap'];

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
          Bienvenue sur TAKA OS
        </h1>
        <p className="text-center text-gray-500 mb-8">
          Configurez votre profil entreprise en quelques etapes
        </p>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {stepLabels.map((label, i) => (
              <span
                key={label}
                className={`text-xs font-medium ${
                  i + 1 <= step ? 'text-blue-600' : 'text-gray-400'
                }`}
              >
                {label}
              </span>
            ))}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            />
          </div>
          <div className="text-right text-xs text-gray-500 mt-1">
            Etape {step} / 5
          </div>
        </div>

        {/* Formulaire */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8">
          {step === 1 && (
            <Step1Identity form={form} errors={errors} updateField={updateField} />
          )}
          {step === 2 && (
            <Step2Domaine
              form={form}
              errors={errors}
              toggleArrayItem={toggleArrayItem}
            />
          )}
          {step === 3 && (
            <Step3CPV
              form={form}
              errors={errors}
              cpvQuery={cpvQuery}
              setCpvQuery={setCpvQuery}
              cpvResults={cpvResults}
              cpvLoading={cpvLoading}
              addCPV={addCPV}
              removeCPV={removeCPV}
            />
          )}
          {step === 4 && (
            <Step4Contexte
              form={form}
              errors={errors}
              updateField={updateField}
              toggleArrayItem={toggleArrayItem}
            />
          )}
          {step === 5 && <Step5Recap form={form} />}

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            <button
              onClick={goBack}
              disabled={step === 1 || loading}
              className={`px-6 py-2.5 rounded-lg border font-medium text-sm transition-colors ${
                step === 1
                  ? 'border-gray-100 text-gray-300 cursor-not-allowed'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Precedent
            </button>

            {step < 5 ? (
              <button
                onClick={goNext}
                className="px-6 py-2.5 rounded-lg bg-blue-600 text-white font-medium text-sm hover:bg-blue-700 transition-colors"
              >
                Suivant
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2.5 rounded-lg bg-green-600 text-white font-medium text-sm hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading && (
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                )}
                {loading ? 'Creation...' : 'Confirmer et acceder au dashboard'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sous-composants d'etapes
// =============================================================================

function Step1Identity({
  form,
  errors,
  updateField,
}: {
  form: OnboardingFormData;
  errors: Partial<Record<keyof OnboardingFormData, string>>;
  updateField: <K extends keyof OnboardingFormData>(key: K, value: OnboardingFormData[K]) => void;
}) {
  return (
    <div className="space-y-4 animate-fadeIn">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Identite de l'entreprise</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nom de l'entreprise</label>
        <input
          type="text"
          value={form.tenant_name}
          onChange={(e) => updateField('tenant_name', e.target.value)}
          className={`w-full px-3 py-2 rounded-lg border ${
            errors.tenant_name ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          } focus:outline-none focus:ring-2`}
          placeholder="Ex: Dupont Construction SARL"
        />
        {errors.tenant_name && <p className="text-red-500 text-xs mt-1">{errors.tenant_name}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">SIRET (14 chiffres)</label>
        <input
          type="text"
          inputMode="numeric"
          maxLength={14}
          value={form.siret}
          onChange={(e) => updateField('siret', e.target.value.replace(/\D/g, '').slice(0, 14))}
          className={`w-full px-3 py-2 rounded-lg border ${
            errors.siret ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          } focus:outline-none focus:ring-2`}
          placeholder="12345678901234"
        />
        {errors.siret && <p className="text-red-500 text-xs mt-1">{errors.siret}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email de contact</label>
        <input
          type="email"
          value={form.admin_email}
          onChange={(e) => updateField('admin_email', e.target.value)}
          className={`w-full px-3 py-2 rounded-lg border ${
            errors.admin_email ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          } focus:outline-none focus:ring-2`}
          placeholder="contact@entreprise.fr"
        />
        {errors.admin_email && <p className="text-red-500 text-xs mt-1">{errors.admin_email}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nom complet (admin)</label>
        <input
          type="text"
          value={form.admin_full_name}
          onChange={(e) => updateField('admin_full_name', e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Jean Dupont"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
        <input
          type="password"
          value={form.admin_password}
          onChange={(e) => updateField('admin_password', e.target.value)}
          className={`w-full px-3 py-2 rounded-lg border ${
            errors.admin_password ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          } focus:outline-none focus:ring-2`}
          placeholder="8 caracteres minimum"
        />
        {errors.admin_password && <p className="text-red-500 text-xs mt-1">{errors.admin_password}</p>}
      </div>
    </div>
  );
}

function Step2Domaine({
  form,
  errors,
  toggleArrayItem,
}: {
  form: OnboardingFormData;
  errors: Partial<Record<keyof OnboardingFormData, string>>;
  toggleArrayItem: (key: 'domaine_activite', item: string) => void;
}) {
  return (
    <div className="space-y-4 animate-fadeIn">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Domaine d'activite</h2>
      <p className="text-sm text-gray-500 mb-4">Selectionnez un ou plusieurs domaines</p>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {DOMAINES.map((d) => {
          const selected = form.domaine_activite.includes(d);
          return (
            <button
              key={d}
              onClick={() => toggleArrayItem('domaine_activite', d)}
              className={`px-4 py-3 rounded-lg border text-sm font-medium text-center transition-all ${
                selected
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              {d}
            </button>
          );
        })}
      </div>

      {errors.domaine_activite && <p className="text-red-500 text-sm">{errors.domaine_activite}</p>}
    </div>
  );
}

function Step3CPV({
  form,
  errors,
  cpvQuery,
  setCpvQuery,
  cpvResults,
  cpvLoading,
  addCPV,
  removeCPV,
}: {
  form: OnboardingFormData;
  errors: Partial<Record<keyof OnboardingFormData, string>>;
  cpvQuery: string;
  setCpvQuery: (v: string) => void;
  cpvResults: CPVItem[];
  cpvLoading: boolean;
  addCPV: (item: CPVItem) => void;
  removeCPV: (code: string) => void;
}) {
  return (
    <div className="space-y-4 animate-fadeIn">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">CPV cibles</h2>
      <p className="text-sm text-gray-500 mb-4">
        Recherchez et selectionnez jusqu'a 10 codes CPV correspondant a votre activite
      </p>

      {/* Autocomplete */}
      <div className="relative">
        <input
          type="text"
          value={cpvQuery}
          onChange={(e) => setCpvQuery(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder='Tapez "electricite" ou un code CPV...'
        />
        {cpvLoading && (
          <div className="absolute right-3 top-2.5">
            <svg className="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
        )}

        {cpvResults.length > 0 && (
          <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 max-h-60 overflow-auto shadow-lg">
            {cpvResults.map((item) => (
              <li
                key={item.id}
                onClick={() => addCPV(item)}
                className="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm border-b border-gray-100 last:border-0"
              >
                <span className="font-mono text-blue-600 font-medium">{item.cpv_code}</span>
                <span className="text-gray-700 ml-2">{item.label}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Tags selectionnes */}
      <div className="flex flex-wrap gap-2 mt-3">
        {form.cpv_preferences.map((item) => (
          <span
            key={item.cpv_code}
            className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm border border-blue-200"
          >
            {item.cpv_code} — {item.label}
            <button
              onClick={() => removeCPV(item.cpv_code)}
              className="ml-2 text-blue-400 hover:text-blue-600 font-bold"
            >
              ×
            </button>
          </span>
        ))}
      </div>

      {errors.cpv_preferences && <p className="text-red-500 text-sm">{errors.cpv_preferences}</p>}
    </div>
  );
}

function Step4Contexte({
  form,
  errors,
  updateField,
  toggleArrayItem,
}: {
  form: OnboardingFormData;
  errors: Partial<Record<keyof OnboardingFormData, string>>;
  updateField: <K extends keyof OnboardingFormData>(key: K, value: OnboardingFormData[K]) => void;
  toggleArrayItem: (key: 'zones_geo' | 'types_marche_acceptes', item: string) => void;
}) {
  return (
    <div className="space-y-5 animate-fadeIn">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Contexte operationnel</h2>

      {/* Effectif */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Effectif</label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {EFFECTIFS.map((e) => (
            <button
              key={e}
              onClick={() => updateField('effectif', e)}
              className={`px-3 py-2 rounded-lg border text-sm font-medium text-center transition-all ${
                form.effectif === e
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              {e}
            </button>
          ))}
        </div>
        {errors.effectif && <p className="text-red-500 text-xs mt-1">{errors.effectif}</p>}
      </div>

      {/* CA */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Chiffre d'affaires annuel (EUR)</label>
        <input
          type="number"
          min={0}
          value={form.ca_annuel}
          onChange={(e) => updateField('ca_annuel', e.target.value)}
          className={`w-full px-3 py-2 rounded-lg border ${
            errors.ca_annuel ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          } focus:outline-none focus:ring-2`}
          placeholder="500000"
        />
        {errors.ca_annuel && <p className="text-red-500 text-xs mt-1">{errors.ca_annuel}</p>}
      </div>

      {/* Zones geo */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Zones geographiques (departements) — {form.zones_geo.length} selectionne(s)
        </label>
        <div className="grid grid-cols-5 sm:grid-cols-10 gap-2 max-h-48 overflow-y-auto p-2 border border-gray-200 rounded-lg">
          {DEPARTEMENTS.map((d) => {
            const selected = form.zones_geo.includes(d);
            return (
              <button
                key={d}
                onClick={() => toggleArrayItem('zones_geo', d)}
                className={`px-2 py-1.5 rounded text-xs font-medium transition-all ${
                  selected
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {d}
              </button>
            );
          })}
        </div>
        {errors.zones_geo && <p className="text-red-500 text-xs mt-1">{errors.zones_geo}</p>}
      </div>

      {/* Types de marche */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Types de marches acceptes</label>
        <div className="flex flex-wrap gap-2">
          {TYPES_MARCHE.map((t) => {
            const selected = form.types_marche_acceptes.includes(t);
            return (
              <button
                key={t}
                onClick={() => toggleArrayItem('types_marche_acceptes', t)}
                className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                  selected
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                }`}
              >
                {t}
              </button>
            );
          })}
        </div>
        {errors.types_marche_acceptes && (
          <p className="text-red-500 text-xs mt-1">{errors.types_marche_acceptes}</p>
        )}
      </div>
    </div>
  );
}

function Step5Recap({ form }: { form: OnboardingFormData }) {
  return (
    <div className="space-y-4 animate-fadeIn">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recapitulatif</h2>

      <div className="space-y-3 text-sm">
        <RecapRow label="Entreprise" value={form.tenant_name} />
        <RecapRow label="SIRET" value={form.siret} />
        <RecapRow label="Email" value={form.admin_email} />
        <RecapRow label="Domaines" value={form.domaine_activite.join(', ')} />
        <RecapRow label="CPV selectionnes" value={`${form.cpv_preferences.length} code(s)`} />
        <RecapRow label="Effectif" value={form.effectif} />
        <RecapRow label="CA annuel" value={`${Number(form.ca_annuel).toLocaleString('fr-FR')} EUR`} />
        <RecapRow label="Departements" value={`${form.zones_geo.length} selectionne(s)`} />
        <RecapRow label="Types de marche" value={form.types_marche_acceptes.join(', ')} />
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <p className="text-sm text-blue-800">
          En confirmant, vous creez votre compte administrateur et accederez directement a votre dashboard.
        </p>
      </div>
    </div>
  );
}

function RecapRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1 border-b border-gray-100 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-900">{value || '-'}</span>
    </div>
  );
}
