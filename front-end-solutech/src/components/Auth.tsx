/**
 * =============================================================================
 * PAGE D'AUTHENTIFICATION
 * Interface adaptée aux écrans mobiles, support Opera Mini
 * Sélection du rôle pour démonstration (en production : détection automatique)
 * =============================================================================
 */

import { useState } from 'react';
import { School, Eye, EyeOff, Shield, User, GraduationCap, Users } from 'lucide-react';
import type { UserRole } from '@/types';
import { useApp } from '@/context/AppContext';

const ROLES: { value: UserRole; label: string; icon: React.ReactNode; desc: string }[] = [
  { value: 'DIRECTEUR', label: 'Directeur', icon: <Shield className="w-5 h-5" />, desc: 'Gestion complète de l\'établissement' },
  { value: 'ADMIN', label: 'Administrateur', icon: <Shield className="w-5 h-5" />, desc: 'Configuration système et utilisateurs' },
  { value: 'ENSEIGNANT', label: 'Enseignant', icon: <GraduationCap className="w-5 h-5" />, desc: 'Notes, présences et bulletins' },
  { value: 'ELEVE', label: 'Élève', icon: <User className="w-5 h-5" />, desc: 'Consultation des résultats' },
  { value: 'PARENT', label: 'Parent', icon: <Users className="w-5 h-5" />, desc: 'Suivi scolaire des enfants' },
];

export function Auth() {
  const { login } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('DIRECTEUR');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulation latence réseau 3G
    setTimeout(() => {
      const success = login(email, password, role);
      if (!success) {
        setError('Identifiants incorrects. Essayez les comptes de démonstration ci-dessous.');
      }
      setLoading(false);
    }, 800);
  };

  const fillDemo = (demoEmail: string, demoRole: UserRole) => {
    setEmail(demoEmail);
    setRole(demoRole);
    setPassword('demo123');
    setError('');
  };

  return (
    <div className="min-h-screen bg-base-200 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo et titre */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-4 shadow-lg">
            <School className="w-8 h-8 text-primary-content" />
          </div>
          <h1 className="text-2xl font-bold text-base-content">SOLUTECH</h1>
          <p className="text-sm text-base-content/60 mt-1">
            Gestion Scolaire - République du Congo
          </p>
          <div className="badge badge-primary badge-sm mt-2">v2.0 · Mode Hors-Ligne</div>
        </div>

        {/* Carte de connexion */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body p-6">
            <h2 className="card-title text-lg justify-center mb-4">Connexion</h2>

            {error && (
              <div className="alert alert-error alert-sm text-sm mb-4">
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Sélection du rôle */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text text-sm font-medium">Rôle</span>
                </label>
                <select
                  className="select select-bordered select-sm w-full"
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  required
                >
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Email */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text text-sm font-medium">Email</span>
                </label>
                <input
                  type="email"
                  className="input input-bordered input-sm w-full"
                  placeholder="nom@ecole.cg"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              {/* Mot de passe */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text text-sm font-medium">Mot de passe</span>
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="input input-bordered input-sm w-full pr-10"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-base-content/50"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-sm w-full"
                disabled={loading}
              >
                {loading ? <span className="loading loading-spinner loading-xs" /> : 'Se connecter'}
              </button>
            </form>

            {/* Comptes démo rapides */}
            <div className="divider text-xs text-base-content/50">Comptes de démonstration</div>
            <div className="grid grid-cols-1 gap-2">
              {ROLES.slice(0, 3).map((r) => {
                const demoEmail = mockEmails[r.value];
                return (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => fillDemo(demoEmail, r.value)}
                    className={`btn btn-outline btn-xs justify-start gap-2 ${role === r.value ? 'btn-active' : ''}`}
                  >
                    {r.icon}
                    <span className="flex-1 text-left">{r.label}</span>
                    <span className="text-[10px] opacity-60 truncate max-w-[140px]">{demoEmail}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer légal */}
        <p className="text-[10px] text-center text-base-content/40 mt-4 px-4">
          Conforme à la Constitution de la République du Congo, art. 29 · Données hébergées sur le continent africain
        </p>
      </div>
    </div>
  );
}

/** Emails de démonstration par rôle */
const mockEmails: Record<string, string> = {
  DIRECTEUR: 'directeur@ecole-marien-ngouabi.cg',
  ADMIN: 'admin@solutech.cg',
  ENSEIGNANT: 'p.okombi@ecole.cg',
  ELEVE: '',
  PARENT: '',
};
