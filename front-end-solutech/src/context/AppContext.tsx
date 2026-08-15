/**
 * =============================================================================
 * CONTEXTE GLOBAL SOLUTECH
 * Gestion de l'état : authentification, données, mode hors-ligne, rôles
 * =============================================================================
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { Utilisateur, Etablissement, UserRole, Eleve, Enseignant, Note, Presence, Classe } from '@/types';
import { mockUtilisateurs, mockEtablissements, mockEleves, mockEnseignants, mockNotes, mockPresences, mockClasses } from '@/data/mockData';
import { useOffline } from '@/hooks/useOffline';
import { createLocalEntity } from '@/utils/sync';

interface AppContextType {
  // Auth
  utilisateur: Utilisateur | null;
  login: (email: string, password: string, role: UserRole) => boolean;
  logout: () => void;
  isAuthenticated: boolean;

  // Données
  etablissement: Etablissement | null;
  eleves: Eleve[];
  enseignants: Enseignant[];
  notes: Note[];
  presences: Presence[];
  classes: Classe[];

  // Actions CRUD (avec sync offline)
  addEleve: (eleve: Omit<Eleve, 'id' | 'syncStatus'>) => void;
  updateEleve: (id: string, data: Partial<Eleve>) => void;
  addNote: (note: Omit<Note, 'id' | 'syncStatus'>) => void;
  addPresence: (presence: Omit<Presence, 'id' | 'syncStatus'>) => void;

  // Offline
  isOnline: boolean;
  isSyncing: boolean;
  pendingCount: number;
  failedCount: number;
  syncError: string | null;
  lastSync: string | null;
  forceSync: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const AUTH_KEY = 'solutech_auth';

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [utilisateur, setUtilisateur] = useState<Utilisateur | null>(null);
  const [etablissement, setEtablissement] = useState<Etablissement | null>(null);
  const [eleves, setEleves] = useState<Eleve[]>(mockEleves);
  const [enseignants, _setEnseignants] = useState<Enseignant[]>(mockEnseignants);
  const [classes] = useState<Classe[]>(mockClasses);
  const [notes, setNotes] = useState<Note[]>(mockNotes);
  const [presences, setPresences] = useState<Presence[]>(mockPresences);

  const { isOnline, isSyncing, pendingCount, failedCount, syncError, lastSync, queueForSync, forceSync } = useOffline();

  // Restauration de la session au démarrage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(AUTH_KEY);
      if (!saved) return;
      const parsed = JSON.parse(saved) as { userId: string };
      const user = mockUtilisateurs.find((u) => u.id === parsed.userId);
      if (user) {
        setUtilisateur(user);
        const etab = mockEtablissements.find((e) => e.id === user.etablissementId);
        if (etab) setEtablissement(etab);
      }
    } catch (err) {
      console.error('[Auth] Session locale illisible, réinitialisation', err);
      try {
        localStorage.removeItem(AUTH_KEY);
      } catch {
        // stockage indisponible : rien de plus à faire
      }
    }
  }, []);

  const login = useCallback((email: string, _password: string, role: UserRole): boolean => {
    // Simulation d'authentification locale
    const user = mockUtilisateurs.find(
      (u) => u.email.toLowerCase() === email.toLowerCase() && u.role === role
    );
    if (user) {
      setUtilisateur(user);
      try {
        localStorage.setItem(AUTH_KEY, JSON.stringify({ userId: user.id, timestamp: Date.now() }));
      } catch (err) {
        // Session non persistée : l'utilisateur devra se reconnecter au prochain démarrage
        console.error('[Auth] Session non persistée (stockage local indisponible)', err);
      }
      const etab = mockEtablissements.find((e) => e.id === user.etablissementId);
      if (etab) setEtablissement(etab);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    setUtilisateur(null);
    setEtablissement(null);
    try {
      localStorage.removeItem(AUTH_KEY);
    } catch (err) {
      console.error('[Auth] Suppression de la session locale impossible', err);
    }
  }, []);

  const addEleve = useCallback((eleveData: Omit<Eleve, 'id' | 'syncStatus'>) => {
    const newEleve: Eleve = createLocalEntity('e', eleveData, isOnline);
    // Une mise en file échouée doit se voir : statut ERROR au lieu de PENDING
    if (!isOnline && !queueForSync({ entityType: 'ELEVE', action: 'CREATE', payload: newEleve })) {
      newEleve.syncStatus = 'ERROR';
    }
    setEleves((prev) => [...prev, newEleve]);
  }, [isOnline, queueForSync]);

  const updateEleve = useCallback((id: string, data: Partial<Eleve>) => {
    let syncStatus: Eleve['syncStatus'] = isOnline ? 'SYNCED' : 'PENDING';
    if (!isOnline && !queueForSync({ entityType: 'ELEVE', action: 'UPDATE', payload: { id, ...data } })) {
      syncStatus = 'ERROR';
    }
    setEleves((prev) =>
      prev.map((e) => (e.id === id ? { ...e, ...data, syncStatus } : e))
    );
  }, [isOnline, queueForSync]);

  const addNote = useCallback((noteData: Omit<Note, 'id' | 'syncStatus'>) => {
    const newNote: Note = createLocalEntity('n', noteData, isOnline);
    if (!isOnline && !queueForSync({ entityType: 'NOTE', action: 'CREATE', payload: newNote })) {
      newNote.syncStatus = 'ERROR';
    }
    setNotes((prev) => [...prev, newNote]);
  }, [isOnline, queueForSync]);

  const addPresence = useCallback((presenceData: Omit<Presence, 'id' | 'syncStatus'>) => {
    const newPresence: Presence = createLocalEntity('p', presenceData, isOnline);
    if (!isOnline && !queueForSync({ entityType: 'PRESENCE', action: 'CREATE', payload: newPresence })) {
      newPresence.syncStatus = 'ERROR';
    }
    setPresences((prev) => [...prev, newPresence]);
  }, [isOnline, queueForSync]);

  const value: AppContextType = {
    utilisateur,
    login,
    logout,
    isAuthenticated: !!utilisateur,
    etablissement,
    eleves,
    enseignants,
    classes,
    notes,
    presences,
    addEleve,
    updateEleve,
    addNote,
    addPresence,
    isOnline,
    isSyncing,
    pendingCount,
    failedCount,
    syncError,
    lastSync,
    forceSync,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp doit être utilisé dans un AppProvider');
  return ctx;
}
