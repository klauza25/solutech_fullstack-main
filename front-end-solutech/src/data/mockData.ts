/**
 * =============================================================================
 * DONNÉES MOCK - Contexte République du Congo
 * Noms réalistes avec accents, villes congolaises, structure MEPSA/MESRSIT
 * =============================================================================
 */

import type {
  Etablissement,
  Classe,
  Eleve,
  Enseignant,
  Matiere,
  Note,
  Presence,
  SeanceCours,
  Utilisateur,
} from '@/types';

/** Année scolaire en cours */
export const ANNEE_SCOLAIRE = '2024-2025';

/** ==========================================================================
 *  UTILISATEURS
 * ========================================================================== */

export const mockUtilisateurs: Utilisateur[] = [
  {
    id: 'u1',
    nom: 'Moussa',
    prenom: 'Jean-Roger',
    email: 'directeur@ecole-marien-ngouabi.cg',
    telephone: '+242 05 512 34 56',
    role: 'DIRECTEUR',
    etablissementId: 'etab1',
    actif: true,
    derniereConnexion: new Date().toISOString(),
    createdAt: '2023-09-01T00:00:00Z',
  },
  {
    id: 'u2',
    nom: 'Boungouéré',
    prenom: 'Marie-Claire',
    email: 'admin@solutech.cg',
    telephone: '+242 06 723 45 67',
    role: 'ADMIN',
    etablissementId: 'etab1',
    actif: true,
    derniereConnexion: new Date().toISOString(),
    createdAt: '2023-09-01T00:00:00Z',
  },
  {
    id: 'u3',
    nom: 'Okombi',
    prenom: 'Patrice',
    email: 'p.okombi@ecole.cg',
    telephone: '+242 05 834 56 78',
    role: 'ENSEIGNANT',
    etablissementId: 'etab1',
    actif: true,
    derniereConnexion: new Date().toISOString(),
    createdAt: '2023-09-01T00:00:00Z',
  },
  {
    id: 'u4',
    nom: 'Tchicaya',
    prenom: 'Antoinette',
    email: 'a.tchicaya@ecole.cg',
    telephone: '+242 06 945 67 89',
    role: 'ENSEIGNANT',
    etablissementId: 'etab1',
    actif: true,
    derniereConnexion: new Date().toISOString(),
    createdAt: '2023-09-01T00:00:00Z',
  },
];

/** ==========================================================================
 *  ÉTABLISSEMENTS
 * ========================================================================== */

export const mockEtablissements: Etablissement[] = [
  {
    id: 'etab1',
    nom: 'École Primaire Marien Ngouabi',
    codeMEPSA: 'CG-BZV-EP-001',
    type: 'PRIMAIRE',
    adresse: 'Rue de l\'Indépendance, Quartier Poto-Poto',
    ville: 'Brazzaville',
    departement: 'Pool',
    telephone: '+242 05 512 34 56',
    email: 'contact@marien-ngouabi.cg',
    directeurId: 'u1',
    nombreEleves: 342,
    nombreEnseignants: 18,
    actif: true,
  },
  {
    id: 'etab2',
    nom: 'Collège d\'Enseignement Général Félix Tshisekedi',
    codeMEPSA: 'CG-PNR-CEG-045',
    type: 'SECONDAIRE_1',
    adresse: 'Avenue Charles de Gaulle',
    ville: 'Pointe-Noire',
    departement: 'Kouilou',
    telephone: '+242 05 623 45 67',
    email: 'contact@ceg-pointenoire.cg',
    directeurId: 'u5',
    nombreEleves: 528,
    nombreEnseignants: 32,
    actif: true,
  },
  {
    id: 'etab3',
    nom: 'Lycée Technique Industriel de Dolisie',
    codeMEPSA: 'CG-DOL-LT-012',
    type: 'TECHNIQUE',
    adresse: 'Boulevard du 28 Août',
    ville: 'Dolisie',
    departement: 'Niari',
    telephone: '+242 05 734 56 78',
    email: 'contact@lti-dolisie.cg',
    directeurId: 'u6',
    nombreEleves: 215,
    nombreEnseignants: 24,
    actif: true,
  },
];

/** ==========================================================================
 *  CLASSES
 * ========================================================================== */

export const mockClasses: Classe[] = [
  // Brazzaville - Primaire
  { id: 'c1', nom: 'CP', niveau: 'PRIMAIRE', etablissementId: 'etab1', enseignantPrincipalId: 'ens1', capaciteMax: 45, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Salle A1' },
  { id: 'c2', nom: 'CE1', niveau: 'PRIMAIRE', etablissementId: 'etab1', enseignantPrincipalId: 'ens2', capaciteMax: 45, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Salle A2' },
  { id: 'c3', nom: 'CE2', niveau: 'PRIMAIRE', etablissementId: 'etab1', enseignantPrincipalId: 'ens3', capaciteMax: 45, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Salle B1' },
  { id: 'c4', nom: 'CM1', niveau: 'PRIMAIRE', etablissementId: 'etab1', enseignantPrincipalId: 'ens4', capaciteMax: 45, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Salle B2' },
  { id: 'c5', nom: 'CM2', niveau: 'PRIMAIRE', etablissementId: 'etab1', enseignantPrincipalId: 'ens1', capaciteMax: 45, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Salle C1' },
  // Pointe-Noire - Secondaire
  { id: 'c6', nom: '6eme', niveau: 'SECONDAIRE_1', etablissementId: 'etab2', enseignantPrincipalId: 'ens5', capaciteMax: 50, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Bloc A - 101' },
  { id: 'c7', nom: '3eme', niveau: 'SECONDAIRE_1', etablissementId: 'etab2', enseignantPrincipalId: 'ens6', capaciteMax: 50, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Bloc A - 102' },
  { id: 'c8', nom: 'Terminale', niveau: 'SECONDAIRE_2', etablissementId: 'etab2', enseignantPrincipalId: 'ens7', capaciteMax: 40, anneeScolaire: ANNEE_SCOLAIRE, salle: 'Bloc B - 201' },
];

/** ==========================================================================
 *  ENSEIGNANTS
 * ========================================================================== */

export const mockEnseignants: Enseignant[] = [
  {
    id: 'ens1',
    matricule: 'ENS-BZV-2018-0042',
    nom: 'Moussa',
    prenom: 'Jean-Roger',
    sexe: 'M',
    telephone: '+242 05 512 34 56',
    email: 'j.moussa@ecole.cg',
    specialite: 'Pédagogie Générale',
    diplome: 'Licence en Sciences de l\'Éducation',
    etablissementId: 'etab1',
    classesIds: ['c1', 'c5'],
    matieres: ['Mathématiques', 'Sciences'],
    dateRecrutement: '2018-09-01',
    actif: true,
  },
  {
    id: 'ens2',
    matricule: 'ENS-BZV-2020-0089',
    nom: 'Boungouéré',
    prenom: 'Marie-Claire',
    sexe: 'F',
    telephone: '+242 06 723 45 67',
    email: 'mc.boungouere@ecole.cg',
    specialite: 'Langue Française',
    diplome: 'Master en Lettres Modernes',
    etablissementId: 'etab1',
    classesIds: ['c2'],
    matieres: ['Français', 'Histoire-Géographie'],
    dateRecrutement: '2020-09-01',
    actif: true,
  },
  {
    id: 'ens3',
    matricule: 'ENS-BZV-2019-0067',
    nom: 'Okombi',
    prenom: 'Patrice',
    sexe: 'M',
    telephone: '+242 05 834 56 78',
    email: 'p.okombi@ecole.cg',
    specialite: 'Mathématiques',
    diplome: 'Licence en Mathématiques',
    etablissementId: 'etab1',
    classesIds: ['c3'],
    matieres: ['Mathématiques', 'Physique-Chimie'],
    dateRecrutement: '2019-09-01',
    actif: true,
  },
  {
    id: 'ens4',
    matricule: 'ENS-BZV-2021-0103',
    nom: 'Tchicaya',
    prenom: 'Antoinette',
    sexe: 'F',
    telephone: '+242 06 945 67 89',
    email: 'a.tchicaya@ecole.cg',
    specialite: 'Sciences Naturelles',
    diplome: 'Licence en Biologie',
    etablissementId: 'etab1',
    classesIds: ['c4'],
    matieres: ['SVT', 'Sciences'],
    dateRecrutement: '2021-09-01',
    actif: true,
  },
  {
    id: 'ens5',
    matricule: 'ENS-PNR-2017-0034',
    nom: 'Makosso',
    prenom: 'Ghislain',
    sexe: 'M',
    telephone: '+242 05 456 78 90',
    email: 'g.makosso@ceg.cg',
    specialite: 'Histoire-Géographie',
    diplome: 'Master en Géographie',
    etablissementId: 'etab2',
    classesIds: ['c6'],
    matieres: ['Histoire-Géographie', 'Éducation Civique'],
    dateRecrutement: '2017-09-01',
    actif: true,
  },
  {
    id: 'ens6',
    matricule: 'ENS-PNR-2019-0078',
    nom: 'Ngouoni',
    prenom: 'Sylvie',
    sexe: 'F',
    telephone: '+242 06 567 89 01',
    email: 's.ngouoni@ceg.cg',
    specialite: 'Langues Étrangères',
    diplome: 'Licence en Anglais',
    etablissementId: 'etab2',
    classesIds: ['c7'],
    matieres: ['Anglais', 'Français'],
    dateRecrutement: '2019-09-01',
    actif: true,
  },
  {
    id: 'ens7',
    matricule: 'ENS-PNR-2015-0012',
    nom: 'Bakala',
    prenom: 'François',
    sexe: 'M',
    telephone: '+242 05 678 90 12',
    email: 'f.bakala@ceg.cg',
    specialite: 'Mathématiques',
    diplome: 'Master en Mathématiques Appliquées',
    etablissementId: 'etab2',
    classesIds: ['c8'],
    matieres: ['Mathématiques', 'Physique'],
    dateRecrutement: '2015-09-01',
    actif: true,
  },
];

/** ==========================================================================
 *  ÉLÈVES - Noms congolais avec accents, contexte réaliste
 * ========================================================================== */

export const mockEleves: Eleve[] = [
  // Classe CP
  {
    id: 'e1',
    matricule: 'ELV-BZV-2024-0001',
    nom: 'Moussavou',
    prenom: 'Kévin',
    sexe: 'M',
    dateNaissance: '2018-03-15',
    lieuNaissance: 'Brazzaville',
    classeId: 'c1',
    etablissementId: 'etab1',
    nomParent: 'Moussavou Jean-Paul',
    telephoneParent: '+242 05 123 45 67',
    adresse: 'Quartier Talangaï, Brazzaville',
    dateInscription: '2024-09-02',
    actif: true,
    syncStatus: 'SYNCED',
    groupeSanguin: 'O+',
  },
  {
    id: 'e2',
    matricule: 'ELV-BZV-2024-0002',
    nom: 'Banzouzi',
    prenom: 'Maëlys',
    sexe: 'F',
    dateNaissance: '2018-07-22',
    lieuNaissance: 'Pointe-Noire',
    classeId: 'c1',
    etablissementId: 'etab1',
    nomParent: 'Banzouzi Cécile',
    telephoneParent: '+242 06 234 56 78',
    adresse: 'Quartier Mfilou, Brazzaville',
    dateInscription: '2024-09-02',
    actif: true,
    syncStatus: 'SYNCED',
  },
  {
    id: 'e3',
    matricule: 'ELV-BZV-2024-0003',
    nom: 'Ngouonimba',
    prenom: 'Loïc',
    sexe: 'M',
    dateNaissance: '2018-01-10',
    lieuNaissance: 'Dolisie',
    classeId: 'c1',
    etablissementId: 'etab1',
    nomParent: 'Ngouonimba François',
    telephoneParent: '+242 05 345 67 89',
    adresse: 'Quartier Ouenzé, Brazzaville',
    dateInscription: '2024-09-03',
    actif: true,
    syncStatus: 'SYNCED',
  },
  // Classe CE1
  {
    id: 'e4',
    matricule: 'ELV-BZV-2023-0045',
    nom: 'Makouala',
    prenom: 'Chloé',
    sexe: 'F',
    dateNaissance: '2017-05-18',
    lieuNaissance: 'Brazzaville',
    classeId: 'c2',
    etablissementId: 'etab1',
    nomParent: 'Makouala Nathalie',
    telephoneParent: '+242 06 456 78 90',
    adresse: 'Quartier Bacongo, Brazzaville',
    dateInscription: '2023-09-04',
    actif: true,
    syncStatus: 'SYNCED',
  },
  {
    id: 'e5',
    matricule: 'ELV-BZV-2023-0046',
    nom: 'Tchibinda',
    prenom: 'Roméo',
    sexe: 'M',
    dateNaissance: '2017-09-30',
    lieuNaissance: 'Brazzaville',
    classeId: 'c2',
    etablissementId: 'etab1',
    nomParent: 'Tchibinda Patrice',
    telephoneParent: '+242 05 567 89 01',
    adresse: 'Quartier Poto-Poto, Brazzaville',
    dateInscription: '2023-09-04',
    actif: true,
    syncStatus: 'SYNCED',
  },
  // Classe CM2 (préparation CEP)
  {
    id: 'e6',
    matricule: 'ELV-BZV-2020-0123',
    nom: 'Mampouya',
    prenom: 'Stéphanie',
    sexe: 'F',
    dateNaissance: '2014-11-08',
    lieuNaissance: 'Brazzaville',
    classeId: 'c5',
    etablissementId: 'etab1',
    nomParent: 'Mampouya Gisèle',
    telephoneParent: '+242 06 678 90 12',
    adresse: 'Quartier Talangaï, Brazzaville',
    dateInscription: '2020-09-07',
    actif: true,
    syncStatus: 'SYNCED',
  },
  {
    id: 'e7',
    matricule: 'ELV-BZV-2020-0124',
    nom: 'Kouilou',
    prenom: 'Bénédicte',
    sexe: 'F',
    dateNaissance: '2014-04-25',
    lieuNaissance: 'Pointe-Noire',
    classeId: 'c5',
    etablissementId: 'etab1',
    nomParent: 'Kouilou André',
    telephoneParent: '+242 05 789 01 23',
    adresse: 'Quartier Mfilou, Brazzaville',
    dateInscription: '2020-09-07',
    actif: true,
    syncStatus: 'SYNCED',
  },
  // Pointe-Noire - 6ème
  {
    id: 'e8',
    matricule: 'ELV-PNR-2024-0201',
    nom: 'Matsiona',
    prenom: 'Jérôme',
    sexe: 'M',
    dateNaissance: '2013-02-14',
    lieuNaissance: 'Pointe-Noire',
    classeId: 'c6',
    etablissementId: 'etab2',
    nomParent: 'Matsiona Léon',
    telephoneParent: '+242 05 890 12 34',
    adresse: 'Quartier Mvoumvou, Pointe-Noire',
    dateInscription: '2024-09-02',
    actif: true,
    syncStatus: 'SYNCED',
  },
  {
    id: 'e9',
    matricule: 'ELV-PNR-2024-0202',
    nom: 'Mouélé',
    prenom: 'Grâce-Divine',
    sexe: 'F',
    dateNaissance: '2013-06-20',
    lieuNaissance: 'Pointe-Noire',
    classeId: 'c6',
    etablissementId: 'etab2',
    nomParent: 'Mouélé Bernadette',
    telephoneParent: '+242 06 901 23 45',
    adresse: 'Quartier Tié-Tié, Pointe-Noire',
    dateInscription: '2024-09-02',
    actif: true,
    syncStatus: 'SYNCED',
  },
  // Pointe-Noire - Terminale
  {
    id: 'e10',
    matricule: 'ELV-PNR-2021-0301',
    nom: 'Boussamba',
    prenom: 'Yvan',
    sexe: 'M',
    dateNaissance: '2007-08-12',
    lieuNaissance: 'Dolisie',
    classeId: 'c8',
    etablissementId: 'etab2',
    nomParent: 'Boussamba Christophe',
    telephoneParent: '+242 05 012 34 56',
    adresse: 'Quartier Mvoumvou, Pointe-Noire',
    dateInscription: '2021-09-06',
    actif: true,
    syncStatus: 'SYNCED',
  },
  {
    id: 'e11',
    matricule: 'ELV-PNR-2021-0302',
    nom: 'Makosso',
    prenom: 'Inès',
    sexe: 'F',
    dateNaissance: '2007-03-05',
    lieuNaissance: 'Pointe-Noire',
    classeId: 'c8',
    etablissementId: 'etab2',
    nomParent: 'Makosso Ghislain',
    telephoneParent: '+242 06 123 45 67',
    adresse: 'Quartier Tié-Tié, Pointe-Noire',
    dateInscription: '2021-09-06',
    actif: true,
    syncStatus: 'SYNCED',
  },
];

/** ==========================================================================
 *  MATIÈRES
 * ========================================================================== */

export const mockMatieres: Matiere[] = [
  { id: 'm1', code: 'FR', nom: 'Français', coefficient: 4, niveau: 'PRIMAIRE' },
  { id: 'm2', code: 'MATH', nom: 'Mathématiques', coefficient: 4, niveau: 'PRIMAIRE' },
  { id: 'm3', code: 'SCI', nom: 'Sciences', coefficient: 2, niveau: 'PRIMAIRE' },
  { id: 'm4', code: 'HG', nom: 'Histoire-Géographie', coefficient: 2, niveau: 'PRIMAIRE' },
  { id: 'm5', code: 'ANG', nom: 'Anglais', coefficient: 2, niveau: 'SECONDAIRE_1' },
  { id: 'm6', code: 'PHYS', nom: 'Physique-Chimie', coefficient: 3, niveau: 'SECONDAIRE_2' },
  { id: 'm7', code: 'SVT', nom: 'SVT', coefficient: 2, niveau: 'SECONDAIRE_2' },
  { id: 'm8', code: 'PHILO', nom: 'Philosophie', coefficient: 2, niveau: 'SECONDAIRE_2' },
  { id: 'm9', code: 'EC', nom: 'Éducation Civique', coefficient: 1, niveau: 'PRIMAIRE' },
];

/** ==========================================================================
 *  NOTES
 * ========================================================================== */

export const mockNotes: Note[] = [
  // Kevin Moussavou - CP - Trimestre 1
  { id: 'n1', eleveId: 'e1', matiereId: 'm1', enseignantId: 'ens2', classeId: 'c1', typeEvaluation: 'DEVOIR', note: 14.5, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-15', appreciation: 'Bon travail, continuer les efforts', syncStatus: 'SYNCED' },
  { id: 'n2', eleveId: 'e1', matiereId: 'm2', enseignantId: 'ens1', classeId: 'c1', typeEvaluation: 'INTERROGATION', note: 16, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-18', appreciation: 'Excellente maîtrise', syncStatus: 'SYNCED' },
  { id: 'n3', eleveId: 'e1', matiereId: 'm3', enseignantId: 'ens3', classeId: 'c1', typeEvaluation: 'DEVOIR', note: 12, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-22', appreciation: 'Doit réviser leçon sur les plantes', syncStatus: 'SYNCED' },
  // Maëlys Banzouzi - CP
  { id: 'n4', eleveId: 'e2', matiereId: 'm1', enseignantId: 'ens2', classeId: 'c1', typeEvaluation: 'DEVOIR', note: 17.5, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-15', appreciation: 'Très bonne expression écrite', syncStatus: 'SYNCED' },
  { id: 'n5', eleveId: 'e2', matiereId: 'm2', enseignantId: 'ens1', classeId: 'c1', typeEvaluation: 'INTERROGATION', note: 15, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-18', syncStatus: 'SYNCED' },
  // Stéphanie Mampouya - CM2
  { id: 'n6', eleveId: 'e6', matiereId: 'm1', enseignantId: 'ens2', classeId: 'c5', typeEvaluation: 'COMPOSITION', note: 13, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-11-05', appreciation: 'Résultat moyen, efforts à fournir', syncStatus: 'SYNCED' },
  { id: 'n7', eleveId: 'e6', matiereId: 'm2', enseignantId: 'ens1', classeId: 'c5', typeEvaluation: 'COMPOSITION', note: 11.5, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-11-05', appreciation: 'Difficultés en géométrie', syncStatus: 'SYNCED' },
  // Yvan Boussamba - Terminale
  { id: 'n8', eleveId: 'e10', matiereId: 'm6', enseignantId: 'ens7', classeId: 'c8', typeEvaluation: 'DEVOIR', note: 10.5, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-10', appreciation: 'Insuffisant pour le bac', syncStatus: 'SYNCED' },
  { id: 'n9', eleveId: 'e10', matiereId: 'm8', enseignantId: 'ens6', classeId: 'c8', typeEvaluation: 'EXAMEN', note: 9, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-11-15', appreciation: 'Révision nécessaire', syncStatus: 'SYNCED' },
  // Inès Makosso - Terminale
  { id: 'n10', eleveId: 'e11', matiereId: 'm6', enseignantId: 'ens7', classeId: 'c8', typeEvaluation: 'DEVOIR', note: 15.5, noteSur: 20, trimestre: 1, anneeScolaire: ANNEE_SCOLAIRE, dateEvaluation: '2024-10-10', appreciation: 'Très bon niveau', syncStatus: 'SYNCED' },
];

/** ==========================================================================
 *  PRÉSENCES
 * ========================================================================== */

export const mockPresences: Presence[] = [
  { id: 'p1', eleveId: 'e1', classeId: 'c1', date: '2024-11-18', statut: 'PRESENT', enseignantId: 'ens1', syncStatus: 'SYNCED' },
  { id: 'p2', eleveId: 'e2', classeId: 'c1', date: '2024-11-18', statut: 'PRESENT', enseignantId: 'ens1', syncStatus: 'SYNCED' },
  { id: 'p3', eleveId: 'e3', classeId: 'c1', date: '2024-11-18', statut: 'ABSENT', justificatif: 'Maladie - certificat médical', enseignantId: 'ens1', syncStatus: 'SYNCED' },
  { id: 'p4', eleveId: 'e4', classeId: 'c2', date: '2024-11-18', statut: 'RETARD', enseignantId: 'ens2', syncStatus: 'SYNCED' },
  { id: 'p5', eleveId: 'e6', classeId: 'c5', date: '2024-11-18', statut: 'PRESENT', enseignantId: 'ens1', syncStatus: 'SYNCED' },
  { id: 'p6', eleveId: 'e8', classeId: 'c6', date: '2024-11-18', statut: 'PRESENT', enseignantId: 'ens5', syncStatus: 'SYNCED' },
  { id: 'p7', eleveId: 'e9', classeId: 'c6', date: '2024-11-18', statut: 'EXCUSE', justificatif: 'Funérailles famille', enseignantId: 'ens5', syncStatus: 'SYNCED' },
];

/** ==========================================================================
 *  EMPLOI DU TEMPS
 * ========================================================================== */

export const mockEmploiDuTemps: SeanceCours[] = [
  { id: 'edt1', classeId: 'c1', matiereId: 'm1', enseignantId: 'ens2', jour: 'LUNDI', heureDebut: '08:00', heureFin: '10:00', salle: 'Salle A1' },
  { id: 'edt2', classeId: 'c1', matiereId: 'm2', enseignantId: 'ens1', jour: 'LUNDI', heureDebut: '10:15', heureFin: '12:15', salle: 'Salle A1' },
  { id: 'edt3', classeId: 'c1', matiereId: 'm3', enseignantId: 'ens3', jour: 'MARDI', heureDebut: '08:00', heureFin: '10:00', salle: 'Salle A1' },
  { id: 'edt4', classeId: 'c2', matiereId: 'm1', enseignantId: 'ens2', jour: 'LUNDI', heureDebut: '08:00', heureFin: '10:00', salle: 'Salle A2' },
  { id: 'edt5', classeId: 'c6', matiereId: 'm5', enseignantId: 'ens6', jour: 'LUNDI', heureDebut: '07:30', heureFin: '09:30', salle: 'Bloc A - 101' },
  { id: 'edt6', classeId: 'c8', matiereId: 'm6', enseignantId: 'ens7', jour: 'LUNDI', heureDebut: '07:30', heureFin: '09:30', salle: 'Bloc B - 201' },
];

/** ==========================================================================
 *  FONCTIONS UTILITAIRES DE RECHERCHE
 * ========================================================================== */

export function getClasseById(id: string): Classe | undefined {
  return mockClasses.find((c) => c.id === id);
}

export function getEleveById(id: string): Eleve | undefined {
  return mockEleves.find((e) => e.id === id);
}

export function getEnseignantById(id: string): Enseignant | undefined {
  return mockEnseignants.find((e) => e.id === id);
}

export function getMatiereById(id: string): Matiere | undefined {
  return mockMatieres.find((m) => m.id === id);
}

export function getEtablissementById(id: string): Etablissement | undefined {
  return mockEtablissements.find((e) => e.id === id);
}

export function getElevesByClasse(classeId: string): Eleve[] {
  return mockEleves.filter((e) => e.classeId === classeId);
}

export function getNotesByEleve(eleveId: string): Note[] {
  return mockNotes.filter((n) => n.eleveId === eleveId);
}

export function getNotesByClasse(classeId: string): Note[] {
  return mockNotes.filter((n) => n.classeId === classeId);
}

export function getPresencesByClasse(classeId: string): Presence[] {
  return mockPresences.filter((p) => p.classeId === classeId);
}

export function getEmploiDuTempsByClasse(classeId: string): SeanceCours[] {
  return mockEmploiDuTemps.filter((e) => e.classeId === classeId);
}
