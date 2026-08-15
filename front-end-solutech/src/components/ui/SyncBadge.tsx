import type { SyncStatus } from '@/types';

const BADGES: Record<SyncStatus, { className: string; label: string }> = {
  SYNCED: { className: 'badge-success', label: 'Sync' },
  PENDING: { className: 'badge-warning', label: 'En attente' },
  ERROR: { className: 'badge-error', label: 'Erreur' },
};

/** Pastille d'état de synchronisation hors-ligne */
export function SyncBadge({ status }: { status: SyncStatus }) {
  const badge = BADGES[status];
  return <span className={`badge badge-xs ${badge.className}`}>{badge.label}</span>;
}
