/**
 * =============================================================================
 * GESTION DES ENSEIGNANTS
 * Annuaire du corps enseignant avec spécialités et classes assignées
 * =============================================================================
 */

import { useState, useMemo } from 'react';
import { Search, GraduationCap, Mail, Phone, BookOpen, Award } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { getClasseById } from '@/data/mockData';

export function TeacherManagement() {
  const { enseignants } = useApp();
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return enseignants.filter((e) =>
      `${e.nom} ${e.prenom} ${e.specialite}`.toLowerCase().includes(search.toLowerCase())
    );
  }, [enseignants, search]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Corps Enseignant</h2>

      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/40" />
            <input
              type="text"
              className="input input-bordered input-sm w-full pl-9"
              placeholder="Rechercher un enseignant..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filtered.map((ens) => (
          <div key={ens.id} className="card bg-base-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="card-body p-4">
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-sm">{ens.prenom} {ens.nom}</h3>
                  <p className="text-[10px] text-base-content/50 font-mono">{ens.matricule}</p>
                  <div className="flex items-center gap-1 mt-1 text-xs text-base-content/70">
                    <Award className="w-3 h-3" />
                    <span>{ens.diplome}</span>
                  </div>
                </div>
                <span className={`badge badge-xs ${ens.sexe === 'F' ? 'badge-secondary' : 'badge-neutral'}`}>
                  {ens.sexe === 'F' ? 'F' : 'M'}
                </span>
              </div>

              <div className="divider my-2" />

              <div className="space-y-1.5 text-xs">
                <div className="flex items-center gap-2 text-base-content/70">
                  <BookOpen className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{ens.specialite} · {ens.matieres.join(', ')}</span>
                </div>
                <div className="flex items-center gap-2 text-base-content/70">
                  <Phone className="w-3.5 h-3.5 shrink-0" />
                  <span>{ens.telephone}</span>
                </div>
                <div className="flex items-center gap-2 text-base-content/70">
                  <Mail className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{ens.email}</span>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-1">
                {ens.classesIds.map((cid) => {
                  const classe = getClasseById(cid);
                  return (
                    <span key={cid} className="badge badge-ghost badge-xs">
                      {classe?.nom ?? cid}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-8 text-base-content/50 text-sm">Aucun enseignant trouvé</div>
      )}
    </div>
  );
}
