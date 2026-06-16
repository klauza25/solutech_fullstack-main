/**
 * =============================================================================
 * PARAMÈTRES ET CONFIGURATION
 * Gestion du compte, sécurité, synchronisation et informations légales
 * =============================================================================
 */

import { useState } from 'react';
import { Shield, Database, Globe, Smartphone, Trash2, RefreshCw, Lock, FileText } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export function Settings() {
  const { utilisateur, isOnline, pendingCount, forceSync, lastSync, logout } = useApp();
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const handleClearData = () => {
    localStorage.clear();
    setShowClearConfirm(false);
    logout();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Paramètres</h2>

      {/* Profil */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary" />
            Mon compte
          </h3>
          <div className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between py-1 border-b border-base-200">
              <span className="text-base-content/60">Nom</span>
              <span className="font-medium">{utilisateur?.prenom} {utilisateur?.nom}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-base-200">
              <span className="text-base-content/60">Rôle</span>
              <span className="badge badge-sm badge-primary">{utilisateur?.role}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-base-200">
              <span className="text-base-content/60">Email</span>
              <span className="font-medium">{utilisateur?.email}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-base-200">
              <span className="text-base-content/60">Téléphone</span>
              <span className="font-medium">{utilisateur?.telephone}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Synchronisation */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" />
            Synchronisation
          </h3>
          <div className="mt-3 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">État de la connexion</p>
                <p className="text-[10px] text-base-content/50">
                  {isOnline ? 'Connecté au serveur' : 'Mode hors-ligne actif'}
                </p>
              </div>
              <div className={`badge ${isOnline ? 'badge-success' : 'badge-error'}`}>
                {isOnline ? 'En ligne' : 'Hors-ligne'}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Données en attente</p>
                <p className="text-[10px] text-base-content/50">
                  {pendingCount === 0 ? 'Tout est synchronisé' : `${pendingCount} modification(s) à envoyer`}
                </p>
              </div>
              <span className="badge badge-sm">{pendingCount}</span>
            </div>

            {lastSync && (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Dernière synchronisation</p>
                  <p className="text-[10px] text-base-content/50">
                    {new Date(lastSync).toLocaleString('fr-FR')}
                  </p>
                </div>
              </div>
            )}

            <button
              onClick={forceSync}
              className="btn btn-outline btn-sm w-full gap-2"
              disabled={!isOnline || pendingCount === 0}
            >
              <RefreshCw className="w-4 h-4" />
              Forcer la synchronisation
            </button>
          </div>
        </div>
      </div>

      {/* Informations système */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm flex items-center gap-2">
            <Smartphone className="w-4 h-4 text-primary" />
            Informations système
          </h3>
          <div className="mt-3 space-y-2 text-xs text-base-content/70">
            <div className="flex items-center gap-2">
              <Globe className="w-3.5 h-3.5" />
              <span>Version : SOLUTECH v2.0</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="w-3.5 h-3.5" />
              <span>Chiffrement des données sensibles : Actif</span>
            </div>
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5" />
              <span>Stockage local : {Math.round(JSON.stringify(localStorage).length / 1024)} Ko utilisés</span>
            </div>
          </div>
        </div>
      </div>

      {/* Conformité légale */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            Conformité légale
          </h3>
          <div className="mt-3 text-xs text-base-content/70 space-y-2">
            <p>
              <strong>Constitution de la République du Congo, art. 29 :</strong>{' '}
              Toute personne a droit au respect de sa vie privée et de sa correspondance.
              Les données des élèves mineurs sont chiffrées et leur accès est strictement contrôlé.
            </p>
            <p>
              <strong>Directives MEPSA/MESRSIT :</strong>{' '}
              La plateforme respecte la structure officielle du système éducatif congolais,
              incluant les cycles maternelle, primaire, secondaire et technique.
            </p>
            <p>
              <strong>Hébergement des données :</strong>{' '}
              Les données sont hébergées sur des serveurs situés sur le continent africain,
              conformément aux accords de transfert de données applicables.
            </p>
          </div>
        </div>
      </div>

      {/* Zone dangereuse */}
      <div className="card bg-base-100 shadow-sm border border-error/30">
        <div className="card-body p-4">
          <h3 className="card-title text-sm text-error">Zone dangereuse</h3>
          {!showClearConfirm ? (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="btn btn-error btn-outline btn-sm w-full gap-2 mt-3"
            >
              <Trash2 className="w-4 h-4" />
              Effacer toutes les données locales
            </button>
          ) : (
            <div className="mt-3 space-y-2">
              <p className="text-xs text-error">
                Attention : Cette action est irréversible. Toutes les données non synchronisées seront perdues.
              </p>
              <div className="flex gap-2">
                <button onClick={() => setShowClearConfirm(false)} className="btn btn-ghost btn-sm flex-1">
                  Annuler
                </button>
                <button onClick={handleClearData} className="btn btn-error btn-sm flex-1">
                  Confirmer la suppression
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
