/**
 * =============================================================================
 * UTILITAIRES D'AFFICHAGE DES DONNÉES SENSIBLES
 * Protection des données des élèves mineurs (Constitution art. 29)
 * =============================================================================
 *
 * Note : aucune clé de chiffrement ne doit vivre côté client. Le chiffrement
 * des données sensibles est assuré par le serveur / le stockage.
 */

/**
 * Hache un identifiant sensible pour l'affichage masqué.
 * Exemple : téléphone parent → +242 05 *** ** 56
 */
export function masquerTelephone(telephone: string): string {
  if (telephone.length < 8) return telephone;
  const debut = telephone.slice(0, 7);
  const fin = telephone.slice(-2);
  return `${debut} *** ** ${fin}`;
}

/**
 * Masque un nom complet pour les aperçus publics.
 */
export function masquerNom(nomComplet: string): string {
  const parts = nomComplet.split(' ');
  return parts
    .map((part, idx) => {
      if (idx === 0) return part;
      return part.charAt(0) + '.'.repeat(part.length - 1);
    })
    .join(' ');
}

/**
 * Vérifie si l'utilisateur a le droit d'accéder aux données sensibles.
 */
export function peutVoirDonneesSensibles(role: string): boolean {
  return ['ADMIN', 'DIRECTEUR', 'ENSEIGNANT'].includes(role);
}
