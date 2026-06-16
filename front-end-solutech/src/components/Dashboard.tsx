/**
 * =============================================================================
 * TABLEAU DE BORD ADAPTATIF
 * Affichage conditionnel selon le rôle de l'utilisateur connecté
 * Statistiques clés, alertes, accès rapides
 * =============================================================================
 */

import {
  Users,
  GraduationCap,
  BookOpen,
  CalendarCheck,
  TrendingUp,
  AlertTriangle,
  WifiOff,
  ArrowRight,
} from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { Link } from 'react-router-dom';

export function Dashboard() {
  const { utilisateur, etablissement, eleves, enseignants, notes, presences, isOnline } = useApp();
  const role = utilisateur?.role;

  // Calculs statistiques
  const totalEleves = eleves.length;
  const totalFilles = eleves.filter((e) => e.sexe === 'F').length;
  const totalGarcons = totalEleves - totalFilles;
  const totalEnseignants = enseignants.length;
  const tauxPresence = presences.length > 0
    ? Math.round((presences.filter((p) => p.statut === 'PRESENT').length / presences.length) * 100)
    : 0;
  const moyenneGenerale = notes.length > 0
    ? (notes.reduce((acc, n) => acc + (n.note / n.noteSur) * 20, 0) / notes.length).toFixed(1)
    : '0';

  // Alertes générées automatiquement
  const elevesAbscents = presences.filter((p) => p.statut === 'ABSENT');
  const notesFaibles = notes.filter((n) => (n.note / n.noteSur) * 20 < 10);

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h2 className="text-xl font-bold">
          Bonjour, {utilisateur?.prenom} {utilisateur?.nom}
        </h2>
        <p className="text-sm text-base-content/60">
          {etablissement?.nom} · {etablissement?.ville} · Année scolaire 2024-2025
        </p>
      </div>

      {/* Alerte hors-ligne */}
      {!isOnline && (
        <div className="alert alert-warning alert-sm">
          <WifiOff className="w-4 h-4" />
          <span>
            Mode hors-ligne activé. Vos modifications seront synchronisées automatiquement à la reconnexion.
          </span>
        </div>
      )}

      {/* Statistiques - visible pour tous les rôles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Élèves"
          value={totalEleves.toString()}
          sub={`${totalFilles} filles · ${totalGarcons} garçons`}
          color="bg-blue-500"
        />
        <StatCard
          icon={<GraduationCap className="w-5 h-5" />}
          label="Enseignants"
          value={totalEnseignants.toString()}
          sub="Corps enseignant"
          color="bg-emerald-500"
        />
        <StatCard
          icon={<CalendarCheck className="w-5 h-5" />}
          label="Présence"
          value={`${tauxPresence}%`}
          sub="Aujourd'hui"
          color="bg-amber-500"
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Moyenne"
          value={moyenneGenerale}
          sub="Générale"
          color="bg-violet-500"
        />
      </div>

      {/* Contenu spécifique au rôle */}
      {role === 'ADMIN' || role === 'DIRECTEUR' ? (
        <AdminDashboard
          elevesAbscents={elevesAbscents.length}
          notesFaibles={notesFaibles.length}
        />
      ) : role === 'ENSEIGNANT' ? (
        <EnseignantDashboard />
      ) : role === 'ELEVE' || role === 'PARENT' ? (
        <EleveDashboard />
      ) : null}

      {/* Section conformité et sécurité */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm">Conformité & Sécurité</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2">
            <div className="flex items-start gap-2 text-xs text-base-content/70">
              <div className="w-2 h-2 rounded-full bg-success mt-1 shrink-0" />
              <span>Données des élèves chiffrées côté client (Constitution art. 29)</span>
            </div>
            <div className="flex items-start gap-2 text-xs text-base-content/70">
              <div className="w-2 h-2 rounded-full bg-success mt-1 shrink-0" />
              <span>Serveur hébergé en Afrique conforme au RGPD africain</span>
            </div>
            <div className="flex items-start gap-2 text-xs text-base-content/70">
              <div className="w-2 h-2 rounded-full bg-success mt-1 shrink-0" />
              <span>Accès parental contrôlé et traçable</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** Carte statistique réutilisable */
function StatCard({
  icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub: string;
  color: string;
}) {
  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-4">
        <div className="flex items-center justify-between">
          <div className={`w-9 h-9 ${color} rounded-lg flex items-center justify-center text-white`}>
            {icon}
          </div>
        </div>
        <div className="mt-2">
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-xs text-base-content/60">{label}</p>
          <p className="text-[10px] text-base-content/40 mt-0.5">{sub}</p>
        </div>
      </div>
    </div>
  );
}

/** Dashboard spécifique Admin/Directeur */
function AdminDashboard({ elevesAbscents, notesFaibles }: { elevesAbscents: number; notesFaibles: number }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Alertes */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-warning" />
            Alertes du jour
          </h3>
          <div className="space-y-2 mt-3">
            {elevesAbscents > 0 && (
              <div className="alert alert-warning alert-sm py-2">
                <span className="text-sm">{elevesAbscents} élève(s) absent(s) aujourd'hui</span>
              </div>
            )}
            {notesFaibles > 0 && (
              <div className="alert alert-error alert-sm py-2">
                <span className="text-sm">{notesFaibles} note(s) inférieure(s) à 10/20</span>
              </div>
            )}
            {elevesAbscents === 0 && notesFaibles === 0 && (
              <div className="alert alert-success alert-sm py-2">
                <span className="text-sm">Aucune alerte particulière aujourd'hui</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Accès rapides */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm">Accès rapides</h3>
          <div className="grid grid-cols-1 gap-2 mt-3">
            <QuickLink to="/eleves" icon={<Users className="w-4 h-4" />} label="Gestion des élèves" />
            <QuickLink to="/notes" icon={<BookOpen className="w-4 h-4" />} label="Saisie des notes" />
            <QuickLink to="/presences" icon={<CalendarCheck className="w-4 h-4" />} label="Feuille de présence" />
            <QuickLink to="/statistiques" icon={<TrendingUp className="w-4 h-4" />} label="Rapports statistiques" />
          </div>
        </div>
      </div>
    </div>
  );
}

/** Dashboard spécifique Enseignant */
function EnseignantDashboard() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm">Mes actions</h3>
          <div className="grid grid-cols-1 gap-2 mt-3">
            <QuickLink to="/notes" icon={<BookOpen className="w-4 h-4" />} label="Saisir des notes" />
            <QuickLink to="/presences" icon={<CalendarCheck className="w-4 h-4" />} label="Faire l'appel" />
            <QuickLink to="/eleves" icon={<Users className="w-4 h-4" />} label="Liste de mes élèves" />
          </div>
        </div>
      </div>
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <h3 className="card-title text-sm">Rappels</h3>
          <ul className="text-sm text-base-content/70 space-y-2 mt-3">
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
              Composition du 1er trimestre à préparer
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
              Réunion parents-professeurs le 15 décembre
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
              Bulletin trimestriel à finaliser avant le 20
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

/** Dashboard spécifique Élève/Parent */
function EleveDashboard() {
  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-4">
        <h3 className="card-title text-sm">Mon suivi scolaire</h3>
        <div className="grid grid-cols-1 gap-2 mt-3">
          <QuickLink to="/notes" icon={<BookOpen className="w-4 h-4" />} label="Consulter mes notes" />
          <QuickLink to="/presences" icon={<CalendarCheck className="w-4 h-4" />} label="Mon assiduité" />
        </div>
        <div className="alert alert-info alert-sm mt-4">
          <span className="text-xs">
            En tant que parent/tuteur, vous avez un accès limité aux données de votre enfant conformément à la Constitution, article 29.
          </span>
        </div>
      </div>
    </div>
  );
}

/** Lien rapide réutilisable */
function QuickLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 p-3 rounded-lg bg-base-200 hover:bg-base-300 transition-colors group"
    >
      <div className="text-primary">{icon}</div>
      <span className="text-sm flex-1">{label}</span>
      <ArrowRight className="w-4 h-4 text-base-content/30 group-hover:text-primary transition-colors" />
    </Link>
  );
}
