/**
 * =============================================================================
 * TYPES SOLUTECH v2.0
 * Structure des données conforme au système éducatif congolais (MEPSA/MESRSIT)
 * =============================================================================
 */

/** Niveaux d'enseignement selon la classification officielle congolaise */
export type NiveauEnseignement =
  | 'MATERNELLE'
  | 'PRIMAIRE'
  | 'SECONDAIRE_1'
  | 'SECONDAIRE_2'
  | 'SUPERIEUR'
  | 'TECHNIQUE';

/** Classes du cycle primaire (MEPSA) */
export type ClassePrimaire = 'CP' | 'CE1' | 'CE2' | 'CM1' | 'CM2';

/** Classes du cycle secondaire (MEPSA) */
export type ClasseSecondaire =
  | '6eme'
  | '5eme'
  | '4eme'
  | '3eme'
  | '2nde'
  | '1ere'
  | 'Terminale';

/** Type de classe complet */
export type NomClasse = ClassePrimaire | ClasseSecondaire | string;

/** Rôles utilisateurs avec permissions granulaires */
export type UserRole = 'ADMIN' | 'ENSEIGNANT' | 'ELEVE' | 'PARENT' | 'DIRECTEUR';

/** Sexe pour la saisie démographique */
export type Sexe = 'M' | 'F';

/** Statut de synchronisation hors-ligne */
export type SyncStatus = 'SYNCED' | 'PENDING' | 'ERROR';

/** ==========================================================================
 *  INTERFACES PRINCIPALES
 * ========================================================================== */

/** Représentation d'un utilisateur dans le système */
export interface Utilisateur {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  role: UserRole;
  etablissementId: string;
  actif: boolean;
  derniereConnexion: string;
  createdAt: string;
}

/** Établissement scolaire (école, collège, lycée, institut) */
export interface Etablissement {
  id: string;
  nom: string;
  codeMEPSA: string;
  type: NiveauEnseignement;
  adresse: string;
  ville: string;
  departement: string;
  telephone: string;
  email: string;
  directeurId: string;
  nombreEleves: number;
  nombreEnseignants: number;
  actif: boolean;
}

/** Classe/section dans un établissement */
export interface Classe {
  id: string;
  nom: NomClasse;
  niveau: NiveauEnseignement;
  etablissementId: string;
  enseignantPrincipalId: string;
  capaciteMax: number;
  anneeScolaire: string;
  salle: string;
}

/** Élève avec données sensibles protégées */
export interface Eleve {
  id: string;
  matricule: string;
  nom: string;
  prenom: string;
  sexe: Sexe;
  dateNaissance: string;
  lieuNaissance: string;
  classeId: string;
  etablissementId: string;
  nomParent: string;
  telephoneParent: string;
  adresse: string;
  dateInscription: string;
  actif: boolean;
  syncStatus: SyncStatus;
  /** Données médicales basiques - accès restreint */
  groupeSanguin?: string;
  allergies?: string;
}

/** Enseignant */
export interface Enseignant {
  id: string;
  matricule: string;
  nom: string;
  prenom: string;
  sexe: Sexe;
  telephone: string;
  email: string;
  specialite: string;
  diplome: string;
  etablissementId: string;
  classesIds: string[];
  matieres: string[];
  dateRecrutement: string;
  actif: boolean;
}

/** Matière enseignée */
export interface Matiere {
  id: string;
  code: string;
  nom: string;
  coefficient: number;
  niveau: NiveauEnseignement;
}

/** Note/bulletin */
export interface Note {
  id: string;
  eleveId: string;
  matiereId: string;
  enseignantId: string;
  classeId: string;
  typeEvaluation: 'DEVOIR' | 'INTERROGATION' | 'EXAMEN' | 'COMPOSITION';
  note: number;
  noteSur: number;
  trimestre: 1 | 2 | 3;
  anneeScolaire: string;
  dateEvaluation: string;
  appreciation?: string;
  syncStatus: SyncStatus;
}

/** Présence/absence */
export interface Presence {
  id: string;
  eleveId: string;
  classeId: string;
  date: string;
  statut: 'PRESENT' | 'ABSENT' | 'RETARD' | 'EXCUSE';
  justificatif?: string;
  enseignantId: string;
  syncStatus: SyncStatus;
}

/** Emploi du temps */
export interface SeanceCours {
  id: string;
  classeId: string;
  matiereId: string;
  enseignantId: string;
  jour: 'LUNDI' | 'MARDI' | 'MERCREDI' | 'JEUDI' | 'VENDREDI' | 'SAMEDI';
  heureDebut: string;
  heureFin: string;
  salle: string;
}

/** File d'attente de synchronisation */
export interface SyncQueueItem {
  id: string;
  entityType: 'ELEVE' | 'NOTE' | 'PRESENCE' | 'ENSEIGNANT';
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  payload: unknown;
  timestamp: number;
  retries: number;
  error?: string;
}

/** Statistiques dashboard */
export interface StatistiquesEtablissement {
  totalEleves: number;
  totalFilles: number;
  totalGarcons: number;
  totalEnseignants: number;
  totalClasses: number;
  tauxPresence: number;
  tauxAbandon: number;
  moyenneGenerale: number;
}

/** État de l'application */
export interface AppState {
  utilisateur: Utilisateur | null;
  etablissement: Etablissement | null;
  isOnline: boolean;
  isSyncing: boolean;
  pendingSyncCount: number;
  lastSyncTime: string | null;
}
