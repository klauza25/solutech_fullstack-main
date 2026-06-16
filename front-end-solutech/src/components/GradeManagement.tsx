/**
 * =============================================================================
 * GESTION DES NOTES
 * Saisie, consultation et modification des évaluations
 * Conforme au système de notation congolais (sur 20, coefficients)
 * =============================================================================
 */

import { useState, useMemo } from 'react';
import { Search, Plus, Save, X, BookOpen, TrendingDown, TrendingUp, Minus } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { getEleveById, getMatiereById, getClasseById } from '@/data/mockData';
import type { Note } from '@/types';

export function GradeManagement() {
  const { utilisateur, notes, addNote, eleves, classes } = useApp();
  const [search, setSearch] = useState('');
  const [classeFilter, setClasseFilter] = useState('');
  const [trimestreFilter, setTrimestreFilter] = useState<string>('');
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState<Partial<Note>>({
    eleveId: '',
    matiereId: '',
    typeEvaluation: 'DEVOIR',
    note: 0,
    noteSur: 20,
    trimestre: 1,
    appreciation: '',
  });

  const filteredNotes = useMemo(() => {
    return notes.filter((n) => {
      const eleve = getEleveById(n.eleveId);
      const matchSearch = eleve
        ? `${eleve.nom} ${eleve.prenom}`.toLowerCase().includes(search.toLowerCase())
        : true;
      const matchClasse = classeFilter ? n.classeId === classeFilter : true;
      const matchTrimestre = trimestreFilter ? n.trimestre === Number(trimestreFilter) : true;
      return matchSearch && matchClasse && matchTrimestre;
    });
  }, [notes, search, classeFilter, trimestreFilter]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.eleveId && formData.matiereId && formData.note !== undefined) {
      const eleve = getEleveById(formData.eleveId);
      addNote({
        ...formData,
        enseignantId: utilisateur?.id ?? '',
        classeId: eleve?.classeId ?? '',
        dateEvaluation: new Date().toISOString().split('T')[0],
        anneeScolaire: '2024-2025',
      } as Omit<Note, 'id' | 'syncStatus'>);
      setShowForm(false);
      setFormData({
        eleveId: '',
        matiereId: '',
        typeEvaluation: 'DEVOIR',
        note: 0,
        noteSur: 20,
        trimestre: 1,
        appreciation: '',
      });
    }
  };

  const getNoteColor = (note: number, sur: number) => {
    const sur20 = (note / sur) * 20;
    if (sur20 >= 14) return 'text-success';
    if (sur20 >= 10) return 'text-warning';
    return 'text-error';
  };

  const getNoteIcon = (note: number, sur: number) => {
    const sur20 = (note / sur) * 20;
    if (sur20 >= 14) return <TrendingUp className="w-3.5 h-3.5 text-success" />;
    if (sur20 >= 10) return <Minus className="w-3.5 h-3.5 text-warning" />;
    return <TrendingDown className="w-3.5 h-3.5 text-error" />;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Gestion des Notes</h2>
        {utilisateur?.role !== 'ELEVE' && utilisateur?.role !== 'PARENT' && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary btn-sm gap-2"
          >
            {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {showForm ? 'Annuler' : 'Nouvelle note'}
          </button>
        )}
      </div>

      {/* Formulaire de saisie */}
      {showForm && (
        <div className="card bg-base-100 shadow-sm border border-primary/20">
          <div className="card-body p-4">
            <h3 className="card-title text-sm">Saisir une note</h3>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
              <div className="form-control">
                <label className="label label-text text-xs">Élève *</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.eleveId}
                  onChange={(e) => setFormData({ ...formData, eleveId: e.target.value })}
                  required
                >
                  <option value="">Sélectionner...</option>
                  {eleves.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.prenom} {e.nom} ({getClasseById(e.classeId)?.nom})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Matière *</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.matiereId}
                  onChange={(e) => setFormData({ ...formData, matiereId: e.target.value })}
                  required
                >
                  <option value="">Sélectionner...</option>
                  <option value="m1">Français</option>
                  <option value="m2">Mathématiques</option>
                  <option value="m3">Sciences</option>
                  <option value="m4">Histoire-Géographie</option>
                  <option value="m5">Anglais</option>
                  <option value="m6">Physique-Chimie</option>
                  <option value="m7">SVT</option>
                  <option value="m8">Philosophie</option>
                  <option value="m9">Éducation Civique</option>
                </select>
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Type d'évaluation</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.typeEvaluation}
                  onChange={(e) => setFormData({ ...formData, typeEvaluation: e.target.value as Note['typeEvaluation'] })}
                >
                  <option value="DEVOIR">Devoir</option>
                  <option value="INTERROGATION">Interrogation</option>
                  <option value="EXAMEN">Examen</option>
                  <option value="COMPOSITION">Composition</option>
                </select>
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Note *</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="20"
                  className="input input-bordered input-sm"
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: Number(e.target.value) })}
                  required
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Note sur</label>
                <input
                  type="number"
                  className="input input-bordered input-sm"
                  value={formData.noteSur}
                  onChange={(e) => setFormData({ ...formData, noteSur: Number(e.target.value) })}
                  min="1"
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Trimestre</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.trimestre}
                  onChange={(e) => setFormData({ ...formData, trimestre: Number(e.target.value) as 1 | 2 | 3 })}
                >
                  <option value={1}>1er trimestre</option>
                  <option value={2}>2ème trimestre</option>
                  <option value={3}>3ème trimestre</option>
                </select>
              </div>
              <div className="form-control md:col-span-3">
                <label className="label label-text text-xs">Appréciation</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.appreciation}
                  onChange={(e) => setFormData({ ...formData, appreciation: e.target.value })}
                  placeholder="Commentaire sur l'évaluation..."
                />
              </div>
              <div className="md:col-span-3 flex gap-2 justify-end">
                <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost btn-sm">
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary btn-sm gap-2">
                  <Save className="w-4 h-4" />
                  Enregistrer la note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Filtres */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/40" />
              <input
                type="text"
                className="input input-bordered input-sm w-full pl-9"
                placeholder="Rechercher un élève..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select
              className="select select-bordered select-sm"
              value={classeFilter}
              onChange={(e) => setClasseFilter(e.target.value)}
            >
              <option value="">Toutes les classes</option>
              {classes.map((c: { id: string; nom: string }) => (
                <option key={c.id} value={c.id}>{c.nom}</option>
              ))}
            </select>
            <select
              className="select select-bordered select-sm"
              value={trimestreFilter}
              onChange={(e) => setTrimestreFilter(e.target.value)}
            >
              <option value="">Tous trimestres</option>
              <option value="1">1er</option>
              <option value="2">2ème</option>
              <option value="3">3ème</option>
            </select>
          </div>
        </div>
      </div>

      {/* Liste des notes - mobile */}
      <div className="lg:hidden space-y-3">
        {filteredNotes.map((n) => {
          const eleve = getEleveById(n.eleveId);
          const matiere = getMatiereById(n.matiereId);
          const sur20 = (n.note / n.noteSur) * 20;
          return (
            <div key={n.id} className="card bg-base-100 shadow-sm">
              <div className="card-body p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-sm">{eleve?.prenom} {eleve?.nom}</h4>
                    <p className="text-[10px] text-base-content/50">{getClasseById(n.classeId)?.nom}</p>
                  </div>
                  <div className={`text-xl font-bold ${getNoteColor(n.note, n.noteSur)}`}>
                    {sur20.toFixed(1)}/20
                  </div>
                </div>
                <div className="flex items-center gap-3 mt-2 text-xs text-base-content/70">
                  <span className="flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5" />
                    {matiere?.nom ?? n.matiereId}
                  </span>
                  <span>{n.typeEvaluation}</span>
                  <span>T{n.trimestre}</span>
                </div>
                {n.appreciation && (
                  <p className="text-xs text-base-content/60 mt-2 italic">"{n.appreciation}"</p>
                )}
                <div className="flex items-center gap-1 mt-2">
                  {getNoteIcon(n.note, n.noteSur)}
                  <span className={`text-xs ${getNoteColor(n.note, n.noteSur)}`}>
                    {sur20 >= 14 ? 'Bonne performance' : sur20 >= 10 ? 'Passable' : 'Insuffisant'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
        {filteredNotes.length === 0 && (
          <div className="text-center py-8 text-base-content/50 text-sm">Aucune note trouvée</div>
        )}
      </div>

      {/* Tableau desktop */}
      <div className="hidden lg:block card bg-base-100 shadow-sm overflow-x-auto">
        <table className="table table-sm">
          <thead>
            <tr className="bg-base-200">
              <th>Élève</th>
              <th>Classe</th>
              <th>Matière</th>
              <th>Type</th>
              <th>Note</th>
              <th>Trim.</th>
              <th>Appréciation</th>
              <th>Sync</th>
            </tr>
          </thead>
          <tbody>
            {filteredNotes.map((n) => {
              const eleve = getEleveById(n.eleveId);
              const matiere = getMatiereById(n.matiereId);
              const sur20 = (n.note / n.noteSur) * 20;
              return (
                <tr key={n.id} className="hover:bg-base-200/50">
                  <td className="font-medium">{eleve?.prenom} {eleve?.nom}</td>
                  <td>{getClasseById(n.classeId)?.nom}</td>
                  <td>{matiere?.nom ?? n.matiereId}</td>
                  <td>
                    <span className="badge badge-xs badge-ghost">{n.typeEvaluation}</span>
                  </td>
                  <td className={`font-bold ${getNoteColor(n.note, n.noteSur)}`}>
                    {sur20.toFixed(1)}/20
                  </td>
                  <td>{n.trimestre}</td>
                  <td className="max-w-[200px] truncate text-xs">{n.appreciation ?? '-'}</td>
                  <td>
                    {n.syncStatus === 'PENDING' ? (
                      <span className="badge badge-warning badge-xs">En attente</span>
                    ) : (
                      <span className="badge badge-success badge-xs">Sync</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filteredNotes.length === 0 && (
          <div className="text-center py-8 text-base-content/50 text-sm">Aucune note trouvée</div>
        )}
      </div>
    </div>
  );
}
