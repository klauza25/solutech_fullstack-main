/**
 * =============================================================================
 * UTILITAIRES DE SYNCHRONISATION HORS-LIGNE
 * =============================================================================
 */

import type { SyncStatus } from '@/types';

/**
 * Crée une entité locale : identifiant temporaire + état de synchronisation
 * déduit de la connectivité (SYNCED en ligne, PENDING hors-ligne).
 */
export function createLocalEntity<T extends object>(
  prefix: string,
  data: T,
  isOnline: boolean
): T & { id: string; syncStatus: SyncStatus } {
  return {
    ...data,
    id: `${prefix}-${Date.now()}`,
    syncStatus: isOnline ? 'SYNCED' : 'PENDING',
  };
}
