/**
 * =============================================================================
 * UTILITAIRES DE CHIFFREMENT
 * Protection des données sensibles des élèves mineurs (Constitution art. 29)
 * =============================================================================
 * 
 * Note : En production, utiliser Web Crypto API avec des clés gérées
 * par le serveur. Cette implémentation est une simulation pédagogique
 * pour démontrer l'approche sécurisée côté client.
 */

const SECRET_KEY = 'SOLUTECH-CONGO-2024-MEPSA-MESRSIT';

/**
 * Chiffre une chaîne de texte avec un algorithme de substitution simple.
 * En production : remplacer par AES-GCM via Web Crypto API.
 */
export function chiffrerDonnees(texte: string): string {
  try {
    const encoded = new TextEncoder().encode(texte + SECRET_KEY);
    const base64 = btoa(String.fromCharCode(...encoded));
    return base64;
  } catch {
    // Fallback si caractères non supportés
    return btoa(unescape(encodeURIComponent(texte + SECRET_KEY)));
  }
}

/**
 * Déchiffre une chaîne précédemment chiffrée.
 */
export function dechiffrerDonnees(texteChiffre: string): string {
  try {
    const decoded = atob(texteChiffre);
    const bytes = new Uint8Array(decoded.split('').map((c) => c.charCodeAt(0)));
    const result = new TextDecoder().decode(bytes);
    return result.replace(SECRET_KEY, '');
  } catch {
    return decodeURIComponent(escape(atob(texteChiffre))).replace(SECRET_KEY, '');
  }
}

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
