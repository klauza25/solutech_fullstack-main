/**
 * =============================================================================
 * GESTION DES ÉLÈVES
 * CRUD complet avec recherche, filtres, et mode hors-ligne
 * Support des caractères spéciaux congolais (é, è, ê, ç, ô)
 * =============================================================================
 */

import { useState, useMemo } from 'react';
import { Search, Plus, Edit2, Save, X, Filter, User, Phone, MapPin, Calendar, AlertCircle } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { getClasseById } from '@/data/mockData';
import { masquerTelephone, masquerNom, peutVoirDonneesSensibles } from '@/utils/crypto';
import type { Eleve, Sexe } from '@/types';

export function StudentManagement() {
  const { utilisateur, eleves, addEleve, updateEleve, classes } = useApp();
  const [search, setSearch] = useState('');
  const [classeFilter, setClasseFilter] = useState('');
  const [sexeFilter, setSexeFilter] = useState<Sexe | ''>('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Formulaire
  const [formData, setFormData] = useState<Partial<Eleve>>({
    nom: '',
    prenom: '',
    sexe: 'M',
    dateNaissance: '',
    lieuNaissance: '',
    classeId: '',
    nomParent: '',
    telephoneParent: '',
    adresse: '',
  });

  const canSeeSensitive = peutVoirDonneesSensibles(utilisateur?.role ?? '');

  // Filtrage et recherche
  const filteredEleves = useMemo(() => {
    return eleves.filter((e) => {
      const matchSearch =
        `${e.nom} ${e.prenom} ${e.matricule}`.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').includes(
          search.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        );
      const matchClasse = classeFilter ? e.classeId === classeFilter : true;
      const matchSexe = sexeFilter ? e.sexe === sexeFilter : true;
      return matchSearch && matchClasse && matchSexe;
    });
  }, [eleves, search, classeFilter, sexeFilter]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      updateEleve(editingId, formData);
      setEditingId(null);
    } else {
      if (formData.nom && formData.prenom && formData.classeId) {
        addEleve({
          ...formData,
          matricule: `ELV-AUTO-${Date.now()}`,
          etablissementId: utilisateur?.etablissementId ?? '',
          dateInscription: new Date().toISOString().split('T')[0],
          actif: true,
        } as Omit<Eleve, 'id' | 'syncStatus'>);
      }
    }
    setShowForm(false);
    resetForm();
  };

  const resetForm = () => {
    setFormData({
      nom: '',
      prenom: '',
      sexe: 'M',
      dateNaissance: '',
      lieuNaissance: '',
      classeId: '',
      nomParent: '',
      telephoneParent: '',
      adresse: '',
    });
  };

  const startEdit = (eleve: Eleve) => {
    setFormData({ ...eleve });
    setEditingId(eleve.id);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Gestion des Élèves</h2>
        <button
          onClick={() => {
            setEditingId(null);
            resetForm();
            setShowForm(!showForm);
          }}
          className="btn btn-primary btn-sm gap-2"
        >
          {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showForm ? 'Annuler' : 'Nouvel élève'}
        </button>
      </div>

      {/* Formulaire */}
      {showForm && (
        <div className="card bg-base-100 shadow-sm border border-primary/20">
          <div className="card-body p-4">
            <h3 className="card-title text-sm">
              {editingId ? 'Modifier un élève' : 'Inscrire un nouvel élève'}
            </h3>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              <div className="form-control">
                <label className="label label-text text-xs">Nom *</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  required
                  placeholder="Ex: Moussavou"
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Prénom *</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.prenom}
                  onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                  required
                  placeholder="Ex: Kévin"
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Sexe</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.sexe}
                  onChange={(e) => setFormData({ ...formData, sexe: e.target.value as Sexe })}
                >
                  <option value="M">Masculin</option>
                  <option value="F">Féminin</option>
                </select>
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Classe *</label>
                <select
                  className="select select-bordered select-sm"
                  value={formData.classeId}
                  onChange={(e) => setFormData({ ...formData, classeId: e.target.value })}
                  required
                >
                  <option value="">Sélectionner...</option>
                  {classes.map((c: { id: string; nom: string; niveau: string }) => (
                    <option key={c.id} value={c.id}>
                      {c.nom} ({c.niveau})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Date de naissance</label>
                <input
                  type="date"
                  className="input input-bordered input-sm"
                  value={formData.dateNaissance}
                  onChange={(e) => setFormData({ ...formData, dateNaissance: e.target.value })}
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Lieu de naissance</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.lieuNaissance}
                  onChange={(e) => setFormData({ ...formData, lieuNaissance: e.target.value })}
                  placeholder="Ex: Brazzaville"
                />
              </div>
              <div className="form-control md:col-span-2">
                <label className="label label-text text-xs">Nom du parent/tuteur</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.nomParent}
                  onChange={(e) => setFormData({ ...formData, nomParent: e.target.value })}
                  placeholder="Ex: Moussavou Jean-Paul"
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Téléphone parent</label>
                <input
                  type="tel"
                  className="input input-bordered input-sm"
                  value={formData.telephoneParent}
                  onChange={(e) => setFormData({ ...formData, telephoneParent: e.target.value })}
                  placeholder="+242 05 XXX XX XX"
                />
              </div>
              <div className="form-control">
                <label className="label label-text text-xs">Adresse</label>
                <input
                  type="text"
                  className="input input-bordered input-sm"
                  value={formData.adresse}
                  onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                  placeholder="Quartier, Ville"
                />
              </div>
              <div className="md:col-span-2 flex gap-2 justify-end mt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost btn-sm">
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary btn-sm gap-2">
                  <Save className="w-4 h-4" />
                  {editingId ? 'Mettre à jour' : 'Enregistrer'}
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
                placeholder="Rechercher par nom, prénom ou matricule..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <select
                className="select select-bordered select-sm"
                value={classeFilter}
                onChange={(e) => setClasseFilter(e.target.value)}
              >
                <option value="">Toutes les classes</option>
                {classes.map((c: { id: string; nom: string }) => (
                  <option key={c.id} value={c.id}>
                    {c.nom}
                  </option>
                ))}
              </select>
              <select
                className="select select-bordered select-sm"
                value={sexeFilter}
                onChange={(e) => setSexeFilter(e.target.value as Sexe | '')}
              >
                <option value="">Tous</option>
                <option value="M">Garçons</option>
                <option value="F">Filles</option>
              </select>
            </div>
          </div>
          <p className="text-[10px] text-base-content/50 mt-1 flex items-center gap-1">
            <Filter className="w-3 h-3" />
            {filteredEleves.length} élève(s) trouvé(s)
          </p>
        </div>
      </div>

      {/* Liste des élèves - vue mobile (cartes) et desktop (tableau) */}
      <div className="lg:hidden space-y-3">
        {filteredEleves.map((eleve) => (
          <EleveCard key={eleve.id} eleve={eleve} canSeeSensitive={canSeeSensitive} onEdit={startEdit} />
        ))}
        {filteredEleves.length === 0 && (
          <div className="text-center py-8 text-base-content/50 text-sm">
            Aucun élève trouvé
          </div>
        )}
      </div>

      <div className="hidden lg:block card bg-base-100 shadow-sm overflow-x-auto">
        <table className="table table-sm">
          <thead>
            <tr className="bg-base-200">
              <th>Matricule</th>
              <th>Nom complet</th>
              <th>Classe</th>
              <th>Sexe</th>
              <th>Parent</th>
              <th>Téléphone</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEleves.map((eleve) => (
              <tr key={eleve.id} className="hover:bg-base-200/50">
                <td className="font-mono text-xs">{eleve.matricule}</td>
                <td className="font-medium">
                  {eleve.prenom} {eleve.nom}
                </td>
                <td>{getClasseById(eleve.classeId)?.nom ?? '-'}</td>
                <td>
                  <span className={`badge badge-xs ${eleve.sexe === 'F' ? 'badge-secondary' : 'badge-neutral'}`}>
                    {eleve.sexe === 'F' ? 'F' : 'M'}
                  </span>
                </td>
                <td>{canSeeSensitive ? eleve.nomParent : masquerNom(eleve.nomParent)}</td>
                <td className="font-mono text-xs">
                  {canSeeSensitive ? eleve.telephoneParent : masquerTelephone(eleve.telephoneParent)}
                </td>
                <td>
                  {eleve.syncStatus === 'PENDING' && (
                    <span className="badge badge-warning badge-xs">En attente</span>
                  )}
                  {eleve.syncStatus === 'SYNCED' && (
                    <span className="badge badge-success badge-xs">Sync</span>
                  )}
                </td>
                <td>
                  <button
                    onClick={() => startEdit(eleve)}
                    className="btn btn-ghost btn-xs btn-circle"
                    aria-label={`Modifier ${eleve.prenom} ${eleve.nom}`}
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredEleves.length === 0 && (
          <div className="text-center py-8 text-base-content/50 text-sm">
            Aucun élève trouvé
          </div>
        )}
      </div>
    </div>
  );
}

/** Carte élève pour mobile */
function EleveCard({
  eleve,
  canSeeSensitive,
  onEdit,
}: {
  eleve: Eleve;
  canSeeSensitive: boolean;
  onEdit: (e: Eleve) => void;
}) {
  const classe = getClasseById(eleve.classeId);

  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold ${
              eleve.sexe === 'F' ? 'bg-pink-500' : 'bg-blue-500'
            }`}>
              <User className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm">
                {eleve.prenom} {eleve.nom}
              </h4>
              <p className="text-[10px] text-base-content/50 font-mono">{eleve.matricule}</p>
            </div>
          </div>
          <button
            onClick={() => onEdit(eleve)}
            className="btn btn-ghost btn-xs btn-circle"
            aria-label="Modifier"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
          <div className="flex items-center gap-1.5 text-base-content/70">
            <Calendar className="w-3.5 h-3.5" />
            <span>{classe?.nom ?? '-'}</span>
          </div>
          <div className="flex items-center gap-1.5 text-base-content/70">
            <Phone className="w-3.5 h-3.5" />
            <span>{canSeeSensitive ? eleve.telephoneParent : masquerTelephone(eleve.telephoneParent)}</span>
          </div>
          <div className="flex items-center gap-1.5 text-base-content/70 col-span-2">
            <MapPin className="w-3.5 h-3.5" />
            <span className="truncate">{eleve.adresse}</span>
          </div>
        </div>

        {eleve.syncStatus === 'PENDING' && (
          <div className="flex items-center gap-1.5 mt-2 text-[10px] text-warning">
            <AlertCircle className="w-3 h-3" />
            <span>Modifications en attente de synchronisation</span>
          </div>
        )}
      </div>
    </div>
  );
}
