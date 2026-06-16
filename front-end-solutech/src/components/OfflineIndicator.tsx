/**
 * =============================================================================
 * INDICATEUR DE CONNEXION
 * Badge visuel permanent indiquant l'état réseau et la file de synchronisation
 * =============================================================================
 */

import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export function OfflineIndicator() {
  const { isOnline, isSyncing, pendingCount, lastSync, forceSync } = useApp();

  if (isOnline && pendingCount === 0) {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-success/10 text-success text-xs rounded-full">
        <Wifi className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">En ligne</span>
        {lastSync && (
          <span className="opacity-70 hidden md:inline">
            · Dernière sync : {new Date(lastSync).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
    );
  }

  if (!isOnline) {
    return (
      <button
        onClick={forceSync}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-error/10 text-error text-xs rounded-full animate-pulse"
        aria-label="Mode hors-ligne, appuyer pour synchroniser"
      >
        <WifiOff className="w-3.5 h-3.5" />
        <span>Hors-ligne</span>
        {pendingCount > 0 && (
          <span className="badge badge-error badge-xs text-white">{pendingCount}</span>
        )}
      </button>
    );
  }

  // En ligne mais avec données en attente
  return (
    <button
      onClick={forceSync}
      disabled={isSyncing}
      className="flex items-center gap-1.5 px-3 py-1.5 bg-warning/10 text-warning text-xs rounded-full"
      aria-label="Synchronisation en attente"
    >
      {isSyncing ? (
        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
      ) : (
        <AlertCircle className="w-3.5 h-3.5" />
      )}
      <span>{isSyncing ? 'Sync...' : `${pendingCount} en attente`}</span>
    </button>
  );
}
