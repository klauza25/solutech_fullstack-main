/**
 * =============================================================================
 * HOOK DE GESTION DU MODE HORS-LIGNE
 * Détection réseau, file d'attente de synchronisation, état de connexion
 * =============================================================================
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { SyncQueueItem } from '@/types';

const SYNC_QUEUE_KEY = 'solutech_sync_queue';
const CORRUPT_QUEUE_KEY = 'solutech_sync_queue_corrompue';
const LAST_SYNC_KEY = 'solutech_last_sync';

/** Nombre de tentatives avant de considérer un élément en échec définitif */
const MAX_RETRIES = 3;

/** Erreur de persistance locale (quota dépassé, navigation privée, file illisible) */
export class StorageError extends Error {
  readonly cause?: unknown;

  constructor(message: string, options?: { cause?: unknown }) {
    super(message);
    this.name = 'StorageError';
    this.cause = options?.cause;
  }
}

/**
 * Récupère la file d'attente depuis le localStorage.
 * Une file illisible est mise de côté (et non silencieusement perdue) et l'erreur
 * est remontée à l'appelant pour affichage.
 */
function readQueue(): { items: SyncQueueItem[]; error: StorageError | null } {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(SYNC_QUEUE_KEY);
    if (!raw) return { items: [], error: null };
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error('Format de file inattendu');
    return { items: parsed as SyncQueueItem[], error: null };
  } catch (err) {
    const error = new StorageError(
      "File de synchronisation locale illisible : les données en attente ont été mises de côté pour récupération.",
      { cause: err }
    );
    console.error('[Offline]', error.message, err);
    try {
      if (raw) localStorage.setItem(CORRUPT_QUEUE_KEY, raw);
      localStorage.removeItem(SYNC_QUEUE_KEY);
    } catch (backupErr) {
      console.error('[Offline] Sauvegarde de la file corrompue impossible', backupErr);
    }
    return { items: [], error };
  }
}

/** Sauvegarde la file d'attente. Lève StorageError si l'écriture échoue. */
function saveQueue(queue: SyncQueueItem[]): void {
  try {
    localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(queue));
  } catch (err) {
    throw new StorageError(
      "Écriture locale impossible (stockage plein ou navigation privée) : les modifications hors-ligne ne sont pas conservées.",
      { cause: err }
    );
  }
}

export function useOffline() {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [failedCount, setFailedCount] = useState(0);
  const [syncError, setSyncError] = useState<string | null>(null);
  const syncTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Initialisation
  useEffect(() => {
    const { items, error } = readQueue();
    setPendingCount(items.length);
    setFailedCount(items.filter((item) => item.retries >= MAX_RETRIES).length);
    if (error) setSyncError(error.message);
    try {
      const last = localStorage.getItem(LAST_SYNC_KEY);
      if (last) setLastSync(last);
    } catch (err) {
      console.error('[Offline] Lecture de la dernière synchronisation impossible', err);
    }
  }, []);

  // Écoute des événements réseau
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Déclenchement automatique de la sync après reconnexion
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
      syncTimeoutRef.current = setTimeout(() => {
        void syncData();
      }, 2000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    };
  }, []);

  /**
   * Ajoute un élément à la file d'attente de synchronisation.
   * Retourne false si la mise en file a échoué (donnée non conservée) : l'appelant
   * doit alors signaler l'échec à l'utilisateur plutôt que d'afficher "en attente".
   */
  const queueForSync = useCallback((item: Omit<SyncQueueItem, 'id' | 'timestamp' | 'retries'>): boolean => {
    const { items, error } = readQueue();
    if (error) setSyncError(error.message);

    const newItem: SyncQueueItem = {
      ...item,
      id: `sync-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: Date.now(),
      retries: 0,
    };
    items.push(newItem);
    try {
      saveQueue(items);
    } catch (err) {
      const message = err instanceof StorageError ? err.message : 'Mise en file impossible.';
      console.error('[Offline]', message, err);
      setSyncError(message);
      return false;
    }
    setPendingCount(items.length);
    return true;
  }, []);

  /** Tente de synchroniser les données en attente */
  const syncData = useCallback(async (): Promise<void> => {
    if (!navigator.onLine) return;
    const { items: queue, error: readError } = readQueue();
    if (readError) setSyncError(readError.message);
    if (queue.length === 0) return;

    setIsSyncing(true);
    const remaining: SyncQueueItem[] = [];
    let lastItemError: string | null = null;

    try {
      for (const item of queue) {
        try {
          // Simulation d'envoi au serveur
          await simulateServerSync(item);
          // Succès : on ne garde pas l'item
        } catch (err) {
          const errorMsg = err instanceof Error ? err.message : 'Erreur inconnue';
          lastItemError = errorMsg;
          if (item.retries < MAX_RETRIES) {
            remaining.push({ ...item, retries: item.retries + 1, error: errorMsg });
          } else {
            // Trop d'échecs : on garde en erreur pour audit
            remaining.push({ ...item, error: errorMsg });
          }
        }
      }

      saveQueue(remaining);
      setPendingCount(remaining.length);
      setFailedCount(remaining.filter((item) => item.retries >= MAX_RETRIES).length);
      setSyncError(lastItemError ? `Synchronisation partielle : ${lastItemError}` : null);

      const now = new Date().toISOString();
      try {
        localStorage.setItem(LAST_SYNC_KEY, now);
      } catch (err) {
        console.error('[Offline] Horodatage de synchronisation non conservé', err);
      }
      setLastSync(now);
    } catch (err) {
      // Échec d'écriture : la file reste en mémoire du navigateur uniquement
      const message = err instanceof StorageError ? err.message : 'Synchronisation interrompue.';
      console.error('[Offline]', message, err);
      setSyncError(message);
    } finally {
      // finally : sans cela un échec d'écriture bloquerait l'UI en état "Sync..."
      setIsSyncing(false);
    }
  }, []);

  /** Force une synchronisation manuelle */
  const forceSync = useCallback(() => {
    void syncData();
  }, [syncData]);

  /** Vide la file d'attente (utile pour debug ou reset) */
  const clearQueue = useCallback((): boolean => {
    try {
      saveQueue([]);
    } catch (err) {
      const message = err instanceof StorageError ? err.message : 'Vidage de la file impossible.';
      console.error('[Offline]', message, err);
      setSyncError(message);
      return false;
    }
    setPendingCount(0);
    setFailedCount(0);
    setSyncError(null);
    return true;
  }, []);

  return {
    isOnline,
    isSyncing,
    pendingCount,
    failedCount,
    syncError,
    lastSync,
    queueForSync,
    forceSync,
    clearQueue,
  };
}

/** Simulation d'appel serveur avec latence réaliste (réseau 3G) */
async function simulateServerSync(_item: SyncQueueItem): Promise<void> {
  return new Promise((resolve, reject) => {
    const latency = 800 + Math.random() * 2000; // 0.8s - 2.8s
    setTimeout(() => {
      // 90% de succès pour la démo
      if (Math.random() > 0.1) {
        resolve();
      } else {
        reject(new Error('Timeout réseau - réessayer'));
      }
    }, latency);
  });
}
