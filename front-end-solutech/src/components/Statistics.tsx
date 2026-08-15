/**
 * =============================================================================
 * STATISTIQUES ET RAPPORTS
 * Tableaux de bord analytiques pour la direction et l'administration
 * Indicateurs clés de performance éducative
 * =============================================================================
 */

import { useMemo } from 'react';
import { TrendingUp, Users, GraduationCap, AlertTriangle, BarChart3 } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { StatCard } from '@/components/ui/StatCard';
import { calculerStatistiques, moyenneSur20, pourcentage, repartitionParSexe, SEUIL_BON, SEUIL_ECHEC } from '@/utils/stats';

export function Statistics() {
  const { eleves, enseignants, notes, presences, classes } = useApp();

  const stats = useMemo(
    () => calculerStatistiques({ eleves, enseignants, notes, presences }),
    [eleves, enseignants, notes, presences]
  );

  const statsParClasse = useMemo(() => {
    return classes.map((c) => {
      const elevesClasse = eleves.filter((e) => e.classeId === c.id);
      return {
        classe: c.nom,
        eleves: elevesClasse.length,
        filles: repartitionParSexe(elevesClasse).filles,
        moyenne: moyenneSur20(notes.filter((n) => n.classeId === c.id)),
      };
    });
  }, [classes, eleves, notes]);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Statistiques de l'Établissement</h2>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon={<Users className="w-5 h-5" />} label="Élèves inscrits" value={stats.totalEleves} color="bg-blue-500" />
        <StatCard icon={<GraduationCap className="w-5 h-5" />} label="Enseignants" value={stats.totalEnseignants} color="bg-emerald-500" />
        <StatCard icon={<TrendingUp className="w-5 h-5" />} label="Moyenne générale" value={`${stats.moyenneGenerale.toFixed(1)}/20`} color="bg-violet-500" />
        <StatCard icon={<BarChart3 className="w-5 h-5" />} label="Taux de réussite" value={`${stats.tauxReussite}%`} color="bg-amber-500" />
      </div>

      {/* Démographie */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card bg-base-100 shadow-sm">
          <div className="card-body p-4">
            <h3 className="card-title text-sm">Répartition par sexe</h3>
            <div className="mt-4 space-y-3">
              <BarreProgression label="Filles" value={stats.totalFilles} total={stats.totalEleves} color="bg-pink-500" />
              <BarreProgression label="Garçons" value={stats.totalGarcons} total={stats.totalEleves} color="bg-blue-500" />
            </div>
            <p className="text-[10px] text-base-content/50 mt-3">
              Ratio F/G : {stats.totalGarcons > 0 ? (stats.totalFilles / stats.totalGarcons).toFixed(2) : 'N/A'}
            </p>
          </div>
        </div>

        <div className="card bg-base-100 shadow-sm">
          <div className="card-body p-4">
            <h3 className="card-title text-sm">Indicateurs de vigilance</h3>
            <div className="space-y-2 mt-3">
              <div className="flex items-center justify-between p-2 bg-error/10 rounded-lg">
                <div className="flex items-center gap-2 text-error text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Notes &lt; 10/20</span>
                </div>
                <span className="font-bold text-error">{stats.notesFaibles}</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-warning/10 rounded-lg">
                <div className="flex items-center gap-2 text-warning text-sm">
                  <TrendingUp className="w-4 h-4" />
                  <span>Taux de présence</span>
                </div>
                <span className="font-bold text-warning">{stats.tauxPresence}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tableau par classe */}
      <div className="card bg-base-100 shadow-sm overflow-x-auto">
        <div className="card-body p-4">
          <h3 className="card-title text-sm">Performance par classe</h3>
          <table className="table table-sm mt-3">
            <thead>
              <tr className="bg-base-200">
                <th>Classe</th>
                <th>Effectif</th>
                <th>Filles</th>
                <th>Moyenne classe</th>
                <th>Niveau</th>
              </tr>
            </thead>
            <tbody>
              {statsParClasse.map((s) => (
                <tr key={s.classe} className="hover:bg-base-200/50">
                  <td className="font-medium">{s.classe}</td>
                  <td>{s.eleves}</td>
                  <td>{s.filles}</td>
                  <td className={`font-bold ${s.moyenne >= SEUIL_ECHEC ? 'text-success' : 'text-error'}`}>
                    {s.moyenne.toFixed(1)}/20
                  </td>
                  <td>
                    {s.moyenne >= SEUIL_BON ? 'Bon' : s.moyenne >= SEUIL_ECHEC ? 'Moyen' : 'Faible'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alertes MEPSA */}
      <div className="alert alert-info alert-sm">
        <AlertTriangle className="w-4 h-4" />
        <span className="text-xs">
          Rapport conforme aux directives MEPSA/MESRSIT. Les données sont anonymisées pour les statistiques publiques
          conformément à la Constitution, article 29.
        </span>
      </div>
    </div>
  );
}

function BarreProgression({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  const pct = pourcentage(value, total);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span>{label}</span>
        <span className="font-medium">{value} ({pct}%)</span>
      </div>
      <div className="w-full bg-base-300 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
