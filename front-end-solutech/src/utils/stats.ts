/**
 * =============================================================================
 * CALCULS STATISTIQUES PARTAGÉS
 * Notation congolaise (ramenée sur 20), assiduité et démographie.
 * Utilisés par le tableau de bord, les rapports et la saisie des notes.
 * =============================================================================
 */

import type { Eleve, Note, Presence } from '@/types';

/** Seuil d'échec du système de notation congolais */
export const SEUIL_ECHEC = 10;
/** Seuil de bonne performance */
export const SEUIL_BON = 14;

type NoteBrute = Pick<Note, 'note' | 'noteSur'>;
type PresenceBrute = Pick<Presence, 'statut'>;
type EleveBrut = Pick<Eleve, 'sexe'>;

/** Ramène une note à l'échelle /20 */
export function noteSur20(note: number, noteSur: number): number {
  return noteSur > 0 ? (note / noteSur) * 20 : 0;
}

/** Moyenne /20 d'un ensemble de notes (0 si aucune note) */
export function moyenneSur20(notes: NoteBrute[]): number {
  if (notes.length === 0) return 0;
  const total = notes.reduce((acc, n) => acc + noteSur20(n.note, n.noteSur), 0);
  return total / notes.length;
}

/** Notes inférieures au seuil d'échec */
export function notesFaibles<T extends NoteBrute>(notes: T[]): T[] {
  return notes.filter((n) => noteSur20(n.note, n.noteSur) < SEUIL_ECHEC);
}

/** Pourcentage entier, 0 si le total est nul */
export function pourcentage(valeur: number, total: number): number {
  return total > 0 ? Math.round((valeur / total) * 100) : 0;
}

/** Taux de présence (%) sur un ensemble d'appels */
export function tauxPresence(presences: PresenceBrute[]): number {
  const presents = presences.filter((p) => p.statut === 'PRESENT').length;
  return pourcentage(presents, presences.length);
}

/** Répartition filles / garçons */
export function repartitionParSexe(eleves: EleveBrut[]): { filles: number; garcons: number } {
  const filles = eleves.filter((e) => e.sexe === 'F').length;
  return { filles, garcons: eleves.length - filles };
}

export interface StatistiquesGlobales {
  totalEleves: number;
  totalFilles: number;
  totalGarcons: number;
  totalEnseignants: number;
  tauxPresence: number;
  moyenneGenerale: number;
  notesFaibles: number;
  tauxReussite: number;
}

/** Indicateurs communs au tableau de bord et aux rapports statistiques */
export function calculerStatistiques(donnees: {
  eleves: EleveBrut[];
  enseignants: unknown[];
  notes: NoteBrute[];
  presences: PresenceBrute[];
}): StatistiquesGlobales {
  const { eleves, enseignants, notes, presences } = donnees;
  const { filles, garcons } = repartitionParSexe(eleves);
  const faibles = notesFaibles(notes).length;

  return {
    totalEleves: eleves.length,
    totalFilles: filles,
    totalGarcons: garcons,
    totalEnseignants: enseignants.length,
    tauxPresence: tauxPresence(presences),
    moyenneGenerale: moyenneSur20(notes),
    notesFaibles: faibles,
    tauxReussite: pourcentage(notes.length - faibles, notes.length),
  };
}
