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

  const { isOnline, isSyncing, pendingCount, lastSync, queueForSync, forceSync } = useOffline();

  // Restauration de la session au démarrage
  useEffect(() => {
    const saved = localStorage.getItem(AUTH_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as { userId: string };
        const user = mockUtilisateurs.find((u) => u.id === parsed.userId);
        if (user) {
          setUtilisateur(user);
          const etab = mockEtablissements.find((e) => e.id === user.etablissementId);
          if (etab) setEtablissement(etab);
        }
      } catch {
        localStorage.removeItem(AUTH_KEY);
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
      localStorage.setItem(AUTH_KEY, JSON.stringify({ userId: user.id, timestamp: Date.now() }));
      const etab = mockEtablissements.find((e) => e.id === user.etablissementId);
      if (etab) setEtablissement(etab);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    setUtilisateur(null);
    setEtablissement(null);
    localStorage.removeItem(AUTH_KEY);
  }, []);

  const addEleve = useCallback((eleveData: Omit<Eleve, 'id' | 'syncStatus'>) => {
    const newEleve: Eleve = {
      ...eleveData,
      id: `e-${Date.now()}`,
      syncStatus: isOnline ? 'SYNCED' : 'PENDING',
    };
    setEleves((prev) => [...prev, newEleve]);
    if (!isOnline) {
      queueForSync({ entityType: 'ELEVE', action: 'CREATE', payload: newEleve });
    }
  }, [isOnline, queueForSync]);

  const updateEleve = useCallback((id: string, data: Partial<Eleve>) => {
    setEleves((prev) =>
      prev.map((e) => (e.id === id ? { ...e, ...data, syncStatus: isOnline ? 'SYNCED' : 'PENDING' as const } : e))
    );
    if (!isOnline) {
      queueForSync({ entityType: 'ELEVE', action: 'UPDATE', payload: { id, ...data } });
    }
  }, [isOnline, queueForSync]);

  const addNote = useCallback((noteData: Omit<Note, 'id' | 'syncStatus'>) => {
    const newNote: Note = {
      ...noteData,
      id: `n-${Date.now()}`,
      syncStatus: isOnline ? 'SYNCED' : 'PENDING',
    };
    setNotes((prev) => [...prev, newNote]);
    if (!isOnline) {
      queueForSync({ entityType: 'NOTE', action: 'CREATE', payload: newNote });
    }
  }, [isOnline, queueForSync]);

  const addPresence = useCallback((presenceData: Omit<Presence, 'id' | 'syncStatus'>) => {
    const newPresence: Presence = {
      ...presenceData,
      id: `p-${Date.now()}`,
      syncStatus: isOnline ? 'SYNCED' : 'PENDING',
    };
    setPresences((prev) => [...prev, newPresence]);
    if (!isOnline) {
      queueForSync({ entityType: 'PRESENCE', action: 'CREATE', payload: newPresence });
    }
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
