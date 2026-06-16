/**
 * =============================================================================
 * GESTION DES PRÉSENCES
 * Feuille d'appel numérique avec statistiques en temps réel
 * Optimisé pour saisie rapide sur mobile (gros boutons tactiles)
 * =============================================================================
 */

import { useState, useMemo } from 'react';
import { CalendarCheck, UserCheck, UserX, Clock, AlertCircle, Save, Filter } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { getEleveById, getClasseById } from '@/data/mockData';
import type { Presence } from '@/types';

const STATUTS = [
  { value: 'PRESENT' as const, label: 'Présent', color: 'btn-success', icon: <UserCheck className="w-4 h-4" /> },
  { value: 'ABSENT' as const, label: 'Absent', color: 'btn-error', icon: <UserX className="w-4 h-4" /> },
  { value: 'RETARD' as const, label: 'Retard', color: 'btn-warning', icon: <Clock className="w-4 h-4" /> },
  { value: 'EXCUSE' as const, label: 'Excusé', color: 'btn-info', icon: <AlertCircle className="w-4 h-4" /> },
];

export function AttendanceTracker() {
  const { utilisateur, eleves, presences, addPresence, classes } = useApp();
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedClasse, setSelectedClasse] = useState('');
  const [localPresences, setLocalPresences] = useState<Record<string, Presence['statut']>>({});
  const [justificatifs, setJustificatifs] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);

  const elevesFiltres = useMemo(() => {
    return selectedClasse
      ? eleves.filter((e) => e.classeId === selectedClasse)
      : eleves;
  }, [eleves, selectedClasse]);

  const presencesDuJour = useMemo(() => {
    return presences.filter((p) => p.date === selectedDate);
  }, [presences, selectedDate]);

  const stats = useMemo(() => {
    const total = elevesFiltres.length;
    const presents = presencesDuJour.filter((p) => p.statut === 'PRESENT').length;
    const absents = presencesDuJour.filter((p) => p.statut === 'ABSENT').length;
    const retards = presencesDuJour.filter((p) => p.statut === 'RETARD').length;
    const excuses = presencesDuJour.filter((p) => p.statut === 'EXCUSE').length;
    const nonSaisis = total - presents - absents - retards - excuses;
    return { total, presents, absents, retards, excuses, nonSaisis };
  }, [elevesFiltres, presencesDuJour]);

  const setStatut = (eleveId: string, statut: Presence['statut']) => {
    setLocalPresences((prev) => ({ ...prev, [eleveId]: statut }));
    setSaved(false);
  };

  const saveAll = () => {
    Object.entries(localPresences).forEach(([eleveId, statut]) => {
      const eleve = getEleveById(eleveId);
      if (eleve) {
        addPresence({
          eleveId,
          classeId: eleve.classeId,
          date: selectedDate,
          statut,
          justificatif: justificatifs[eleveId] || undefined,
          enseignantId: utilisateur?.id ?? '',
        });
      }
    });
    setLocalPresences({});
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const getCurrentStatut = (eleveId: string): Presence['statut'] | undefined => {
    if (localPresences[eleveId]) return localPresences[eleveId];
    const saved = presencesDuJour.find((p) => p.eleveId === eleveId);
    return saved?.statut;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Feuille de Présence</h2>
        <button
          onClick={saveAll}
          className="btn btn-primary btn-sm gap-2"
          disabled={Object.keys(localPresences).length === 0}
        >
          <Save className="w-4 h-4" />
          Enregistrer
        </button>
      </div>

      {saved && (
        <div className="alert alert-success alert-sm">
          <CalendarCheck className="w-4 h-4" />
          <span>Présences enregistrées avec succès</span>
        </div>
      )}

      {/* Filtres */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="date"
              className="input input-bordered input-sm"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
            <select
              className="select select-bordered select-sm flex-1"
              value={selectedClasse}
              onChange={(e) => setSelectedClasse(e.target.value)}
            >
              <option value="">Toutes les classes</option>
              {classes.map((c: { id: string; nom: string }) => (
                <option key={c.id} value={c.id}>{c.nom}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <StatBadge label="Total" value={stats.total} color="bg-base-300" />
        <StatBadge label="Présents" value={stats.presents} color="bg-success/20 text-success" />
        <StatBadge label="Absents" value={stats.absents} color="bg-error/20 text-error" />
        <StatBadge label="Retards" value={stats.retards} color="bg-warning/20 text-warning" />
        <StatBadge label="Non saisis" value={stats.nonSaisis} color="bg-info/20 text-info" />
      </div>

      {/* Liste des élèves pour l'appel */}
      <div className="space-y-3">
        {elevesFiltres.map((eleve) => {
          const current = getCurrentStatut(eleve.id);
          const classe = getClasseById(eleve.classeId);
          return (
            <div key={eleve.id} className="card bg-base-100 shadow-sm">
              <div className="card-body p-3 sm:p-4">
                <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-sm">{eleve.prenom} {eleve.nom}</h4>
                      <span className={`badge badge-xs ${eleve.sexe === 'F' ? 'badge-secondary' : 'badge-neutral'}`}>
                        {eleve.sexe}
                      </span>
                    </div>
                    <p className="text-[10px] text-base-content/50">{classe?.nom} · {eleve.matricule}</p>
                  </div>

                  <div className="flex gap-1.5 flex-wrap">
                    {STATUTS.map((s) => (
                      <button
                        key={s.value}
                        onClick={() => setStatut(eleve.id, s.value)}
                        className={`btn btn-xs gap-1 ${s.color} ${current === s.value ? 'btn-active ring-2 ring-offset-1 ring-primary' : 'btn-outline'}`}
                      >
                        {s.icon}
                        <span className="hidden sm:inline">{s.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {(current === 'ABSENT' || current === 'EXCUSE') && (
                  <div className="mt-2">
                    <input
                      type="text"
                      className="input input-bordered input-xs w-full"
                      placeholder="Justificatif (maladie, funérailles, etc.)"
                      value={justificatifs[eleve.id] ?? ''}
                      onChange={(e) => setJustificatifs((prev) => ({ ...prev, [eleve.id]: e.target.value }))}
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {elevesFiltres.length === 0 && (
          <div className="text-center py-8 text-base-content/50 text-sm">
            <Filter className="w-8 h-8 mx-auto mb-2 opacity-50" />
            Sélectionnez une classe pour faire l'appel
          </div>
        )}
      </div>
    </div>
  );
}

function StatBadge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className={`rounded-lg p-2 text-center ${color}`}>
      <p className="text-lg font-bold">{value}</p>
      <p className="text-[10px] opacity-80">{label}</p>
    </div>
  );
}
