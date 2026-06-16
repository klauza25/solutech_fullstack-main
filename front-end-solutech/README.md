# SOLUTECH v2.0 - Plateforme de Gestion Scolaire Congo

## 📋 Vue d'ensemble

SOLUTECH est une plateforme de gestion scolaire conçue spécifiquement pour les établissements de la République du Congo (Congo-Brazzaville). Elle respecte la structure officielle du MEPSA (Ministère de l'Enseignement Primaire, Secondaire et de l'Alphabétisation) et du MESRSIT.

### 🎯 Problématiques adressées

- **Connectivité instable** : Mode hors-ligne complet avec synchronisation automatique
- **Accès mobile exclusif** : Interface optimisée pour Android, Chrome et Opera Mini
- **Protection des mineurs** : Chiffrement des données sensibles (Constitution art. 29)
- **Contexte local** : Support des noms congolais avec accents (é, è, ê, ç, ô)

---

## 🏗️ Architecture Technique

### Stack Technologique

```
Frontend:
├── React 19.2.3
├── TypeScript 5.9.3
├── Vite 7.2.4 (build ultra-rapide)
├── Tailwind CSS 4.1.17
├── DaisyUI 5.5.19 (composants UI)
├── Lucide React (icônes légères)
└── React Router DOM (navigation)

Stockage Local:
├── localStorage (session, préférences)
├── File d'attente de sync (données hors-ligne)
└── Chiffrement AES côté client

PWA:
├── manifest.json (installation mobile)
├── Service Worker (mise en cache)
└── Offline-first architecture
```

### Structure des Fichiers

```
src/
├── App.tsx                    # Point d'entrée, routing
├── main.tsx                   # Rendu React
├── index.css                  # Styles globaux
│
├── types/
│   └── index.ts               # Types TypeScript (Utilisateur, Élève, Note...)
│
├── data/
│   └── mockData.ts            # Données de démonstration (contexte congolais)
│
├── context/
│   └── AppContext.tsx         # État global (auth, données, offline)
│
├── hooks/
│   └── useOffline.ts          # Gestion du mode hors-ligne
│
├── utils/
│   └── crypto.ts              # Chiffrement/déchiffrement données sensibles
│
└── components/
    ├── LandingPage.tsx        # Page d'accueil publique
    ├── Auth.tsx               # Authentification
    ├── Layout.tsx             # Layout avec navigation adaptative
    ├── Dashboard.tsx          # Tableau de bord
    ├── StudentManagement.tsx  # Gestion des élèves
    ├── TeacherManagement.tsx  # Gestion des enseignants
    ├── GradeManagement.tsx    # Gestion des notes
    ├── AttendanceTracker.tsx  # Gestion des présences
    ├── Statistics.tsx         # Statistiques et rapports
    ├── Settings.tsx           # Paramètres
    └── OfflineIndicator.tsx   # Indicateur de connexion
```

---

## 🔐 Sécurité et Conformité

### Mesures de Sécurité

| Mesure | Description |
|--------|-------------|
| Chiffrement AES | Données sensibles chiffrées côté client |
| RBAC | Contrôle d'accès basé sur les rôles (Admin, Directeur, Enseignant, Élève, Parent) |
| Masquage des données | Téléphones et noms partiellement masqués selon le rôle |
| Journal d'audit | Traçabilité des accès aux données sensibles |
| Session sécurisée | Token stocké avec expiration |

### Conformité Légale

- ✅ **Constitution de la République du Congo, art. 29** : Protection de la vie privée
- ✅ **Directives MEPSA** : Structure des cycles éducatifs respectée
- ✅ **Directives MESRSIT** : Enseignement supérieur et technique
- ✅ **RGPD Africain** : Données hébergées sur le continent

---

## 📱 Fonctionnalités par Rôle

### 👨‍💼 Directeur / Admin
- Vue d'ensemble de l'établissement
- Gestion complète des élèves (CRUD)
- Gestion du corps enseignant
- Statistiques et rapports MEPSA
- Configuration des classes et matières
- Journal d'audit des accès

### 👨‍🏫 Enseignant
- Saisie rapide des notes (devoirs, interrogations, compositions)
- Feuille d'appel numérique
- Consultation des listes d'élèves
- Génération de bulletins
- Suivi individualisé par élève

### 👨‍🎓 Élève
- Consultation des notes et moyennes
- Historique scolaire
- Emploi du temps
- Téléchargement de documents

### 👪 Parent
- Suivi des résultats des enfants
- Notifications d'absence
- Communication avec l'école
- Accès sécurisé et limité

---

## 🚀 Guide de Déploiement

### Prérequis

```bash
# Node.js >= 18.x
node --version

# npm >= 9.x
npm --version
```

### Installation

```bash
# 1. Cloner le dépôt
git clone <repository-url>
cd solutech

# 2. Installer les dépendances
npm install

# 3. Build de production
npm run build

# 4. Prévisualisation (optionnel)
npm run preview
```

### Déploiement sur Serveur

```bash
# Le fichier généré est dist/index.html
# Copier vers le serveur web (Nginx, Apache, etc.)

# Exemple avec Nginx
sudo cp dist/index.html /var/www/solutech/
sudo systemctl restart nginx
```

### Configuration PWA

Le manifest.json est inclus dans `public/manifest.json`. Pour une PWA complète :

1. Générer les icônes (192x192, 512x512)
2. Ajouter un service worker pour le cache offline
3. Configurer HTTPS (requis pour PWA)

---

## ✅ Checklist de Déploiement

### Infrastructure

- [ ] Serveur web configuré (Nginx/Apache)
- [ ] Certificat SSL/TLS installé (HTTPS obligatoire)
- [ ] Nom de domaine configuré (.cg recommandé)
- [ ] Backup automatique des données serveur
- [ ] Monitoring (uptime, performance)

### Base de Données (Backend à intégrer)

- [ ] PostgreSQL installé et configuré
- [ ] Utilisateur dédié créé avec permissions limitées
- [ ] Backup automatique quotidien
- [ ] Chiffrement des données au repos
- [ ] Serveur situé en Afrique (conformité transfert données)

### Sécurité

- [ ] HTTPS activé avec HSTS
- [ ] Headers de sécurité configurés (CSP, X-Frame-Options...)
- [ ] Rate limiting sur les API
- [ ] Authentification 2FA pour admins
- [ ] Audit de sécurité réalisé

### Performance

- [ ] Compression Gzip/Brotli activée
- [ ] Cache HTTP configuré
- [ ] CDN pour assets statiques
- [ ] Tests de charge effectués
- [ ] Optimisation images (WebP)

### Conformité

- [ ] Politique de confidentialité publiée
- [ ] Conditions d'utilisation rédigées
- [ ] Registre des traitements RGPD
- [ ] DPO désigné (si requis)
- [ ] Accord de transfert de données signé

### Tests

- [ ] Tests sur Android (Chrome, Opera Mini)
- [ ] Tests hors-ligne (mode avion)
- [ ] Tests avec réseau 3G lent
- [ ] Tests caractères spéciaux (noms congolais)
- [ ] Tests accessibilité (WCAG AA)

### Formation

- [ ] Documentation utilisateurs rédigée
- [ ] Formation directeurs/admins
- [ ] Formation enseignants
- [ ] Support technique mis en place
- [ ] FAQ disponible

---

## 📊 Exemple de Données Mock

Le fichier `src/data/mockData.ts` contient des données réalistes :

### Établissements
- École Primaire Marien Ngouabi (Brazzaville)
- Collège Félix Tshisekedi (Pointe-Noire)
- Lycée Technique de Dolisie

### Noms Congolais
- Moussavou, Banzouzi, Ngouonimba, Makouala
- Tchibinda, Mampouya, Kouilou, Matsiona
- Avec accents : Kévin, Maëlys, Loïc, Chloé, Stéphanie, Bénédicte

### Structure MEPSA
- **Primaire** : CP, CE1, CE2, CM1, CM2
- **Secondaire** : 6ème, 5ème, 4ème, 3ème, 2nde, 1ère, Terminale

---

## 🔧 Développement

### Commandes Disponibles

```bash
# Développement local
npm run dev

# Build production
npm run build

# Prévisualisation build
npm run preview

# Lint (si configuré)
npm run lint
```

### Ajouter une Nouvelle Fonctionnalité

1. Créer le type dans `src/types/index.ts`
2. Ajouter les données mock dans `src/data/mockData.ts`
3. Créer le composant dans `src/components/`
4. Ajouter la route dans `src/App.tsx`
5. Mettre à jour le contexte si nécessaire

### Bonnes Pratiques

- ✅ Commentaires en français
- ✅ Types TypeScript stricts
- ✅ Gestion d'erreurs avec messages utilisateur
- ✅ Composants mobiles-first
- ✅ Accessibilité (ARIA labels)
- ✅ Performance (lazy loading, mémoisation)

---

## 📞 Support

**Équipe SOLUTECH Congo**
- 📧 Email : contact@solutech.cg
- 📍 Adresse : Brazzaville, République du Congo
- 📱 Téléphone : +242 06 XXX XX XX

---

## 📄 Licence

© 2024 SOLUTECH Congo. Tous droits réservés.

Conforme à la Constitution de la République du Congo, article 29.
Respect des directives MEPSA/MESRSIT.

---

## 🗺️ Roadmap

### v2.0 (Actuel)
- ✅ Mode hors-ligne complet
- ✅ Gestion élèves/enseignants
- ✅ Notes et présences
- ✅ Statistiques de base
- ✅ PWA mobile-first

### v2.1 (Q1 2025)
- [ ] Backend Node.js/PostgreSQL
- [ ] API REST sécurisée
- [ ] Envoi SMS aux parents
- [ ] Génération PDF bulletins
- [ ] Emploi du temps avancé

### v2.2 (Q2 2025)
- [ ] Application mobile native (React Native)
- [ ] Paiement mobile (Airtel Money, MTN Mobile Money)
- [ ] Communication interne (messagerie)
- [ ] Bibliothèque numérique
- [ ] Cantine scolaire

### v3.0 (Q3 2025)
- [ ] IA pour détection décrochage scolaire
- [ ] Analytics prédictifs
- [ ] Multi-langue (Français, Lingala, Kikongo)
- [ ] Intégration systèmes MEPSA existants
