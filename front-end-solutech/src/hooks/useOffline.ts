/**
 * =============================================================================
 * HOOK DE GESTION DU MODE HORS-LIGNE
 * Détection réseau, file d'attente de synchronisation, état de connexion
 * =============================================================================
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { SyncQueueItem } from '@/types';

const SYNC_QUEUE_KEY = 'solutech_sync_queue';
const LAST_SYNC_KEY = 'solutech_last_sync';

/** Récupère la file d'attente depuis le localStorage */
function getQueue(): SyncQueueItem[] {
  try {
    const raw = localStorage.getItem(SYNC_QUEUE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/** Sauvegarde la file d'attente */
function saveQueue(queue: SyncQueueItem[]): void {
  localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(queue));
}

export function useOffline() {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const syncTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Initialisation
  useEffect(() => {
    setPendingCount(getQueue().length);
    const last = localStorage.getItem(LAST_SYNC_KEY);
    if (last) setLastSync(last);
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

  /** Ajoute un élément à la file d'attente de synchronisation */
  const queueForSync = useCallback((item: Omit<SyncQueueItem, 'id' | 'timestamp' | 'retries'>) => {
    const queue = getQueue();
    const newItem: SyncQueueItem = {
      ...item,
      id: `sync-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: Date.now(),
      retries: 0,
    };
    queue.push(newItem);
    saveQueue(queue);
    setPendingCount(queue.length);
  }, []);

  /** Tente de synchroniser les données en attente */
  const syncData = useCallback(async (): Promise<void> => {
    if (!navigator.onLine) return;
    const queue = getQueue();
    if (queue.length === 0) return;

    setIsSyncing(true);
    const remaining: SyncQueueItem[] = [];

    for (const item of queue) {
      try {
        // Simulation d'envoi au serveur
        await simulateServerSync(item);
        // Succès : on ne garde pas l'item
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Erreur inconnue';
        if (item.retries < 3) {
          remaining.push({ ...item, retries: item.retries + 1, error: errorMsg });
        } else {
          // Trop d'échecs : on garde en erreur pour audit
          remaining.push({ ...item, error: errorMsg });
        }
      }
    }

    saveQueue(remaining);
    setPendingCount(remaining.length);
    const now = new Date().toISOString();
    localStorage.setItem(LAST_SYNC_KEY, now);
    setLastSync(now);
    setIsSyncing(false);
  }, []);

  /** Force une synchronisation manuelle */
  const forceSync = useCallback(() => {
    void syncData();
  }, [syncData]);

  /** Vide la file d'attente (utile pour debug ou reset) */
  const clearQueue = useCallback(() => {
    saveQueue([]);
    setPendingCount(0);
  }, []);

  return {
    isOnline,
    isSyncing,
    pendingCount,
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
