from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class TypeExamen(models.TextChoices):
	CEPE = "CEPE", _("CEPE + Concours d'entrée en 6ème")
	BEPC = "BEPC", _("BEPC (Brevet d'Études du 1er Cycle)")
	BAC_GENERAL = "BAC_GEN", _("Baccalauréat Général")
	BAC_TECH = "BAC_TECH", _("Baccalauréat Technique")
	BAC_PRO = "BAC_PRO", _("Baccalauréat Professionnel")

class Serie(models.TextChoices):
	L = "L", _("Littéraire")
	S = "S", _("Scientifique")
	ST = "ST", _("Sciences & Technologies")
	SE = "SE", _("Sciences Économiques")
	# Autres séries techniques/pro à ajouter selon besoin

class StatutSession(models.TextChoices):
	PREPARATION = "PREP", _("Préparation / Inscriptions ouvertes")
	EN_COURS = "COURS", _("Examens en cours")
	SAISIE = "SAISIE", _("Saisie des notes")
	PROCLAME = "PROC", _("Résultats proclamés")
	FERME = "FERME", _("Session clôturée")

class Mention(models.TextChoices):
	PASSABLE = "PASS", _("Passable (10-11,99)")
	ASSEZ_BIEN = "AB", _("Assez Bien (12-13,99)")
	BIEN = "B", _("Bien (14-15,99)")
	TRES_BIEN = "TB", _("Très Bien (≥16)")
	AJOURNE = "AJ", _("Ajourné (<10)")
	ADMIS = "ADM", _("Admis (mention non spécifiée)")

class SessionExamen(models.Model):
	"""Session officielle d'examen — CDC §2.3"""
	annee_scolaire = models.CharField(max_length=9, help_text=_("Ex: 2025-2026"))
	type_examen = models.CharField(choices=TypeExamen.choices, max_length=20)
	serie = models.CharField(choices=Serie.choices, max_length=5, null=True, blank=True)
	statut = models.CharField(choices=StatutSession.choices, default=StatutSession.PREPARATION)
	date_debut = models.DateField()
	date_fin = models.DateField()
	est_proclame = models.BooleanField(default=False, help_text=_("Résultats officiels validés par le jury"))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _("Session d'examen")
		constraints = [
			models.UniqueConstraint(
				fields=["annee_scolaire", "type_examen", "serie"],
				name="unique_session_par_annee_type_serie"
			)
		]
		ordering = ["-annee_scolaire", "type_examen"]

	def __str__(self):
		return f"{self.type_examen} {self.annee_scolaire} ({self.get_statut_display()})"


class CandidatExamen(models.Model):
	"""Lien entre un élève/inscrit et une session d'examen"""
	session = models.ForeignKey(SessionExamen, on_delete=models.PROTECT, related_name="candidats")
	eleve = models.ForeignKey("eleves.Eleve", on_delete=models.PROTECT, null=True, blank=True, related_name="candidatures_examens")
	numero_candidat = models.CharField(max_length=30, unique=True, help_text=_("Numéro de table/convocation officiel"))
	centre_examen = models.CharField(max_length=200, help_text=_("Lieu de passage de l'examen"))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _("Candidat")
		ordering = ["session", "numero_candidat"]

	def __str__(self):
		nom = self.eleve.nom if self.eleve else "Candidat libre"
		return f"{self.numero_candidat} — {nom}"


class NoteExamen(models.Model):
	"""Note par épreuve — immuable après proclamation (CDC §7.1)"""
	candidat = models.ForeignKey(CandidatExamen, on_delete=models.CASCADE, related_name="notes")
	matiere = models.CharField(max_length=100, help_text=_("Nom officiel de l'épreuve (ex: Mathématiques, SVT)"))
	coefficient = models.DecimalField(max_digits=3, decimal_places=1)
	note = models.DecimalField(max_digits=4, decimal_places=2, help_text=_("Note sur 20"))
	saisie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("Note d'examen")
		constraints = [
			models.UniqueConstraint(fields=["candidat", "matiere"], name="unique_note_par_candidat_matiere")
		]
		ordering = ["candidat", "matiere"]

	def __str__(self):
		return f"{self.candidat.numero_candidat} | {self.matiere} : {self.note}/20"


class ResultatFinal(models.Model):
	"""Résultat global et mention — calculé automatiquement, verrouillé après proclamation"""
	candidat = models.OneToOneField(CandidatExamen, on_delete=models.CASCADE, primary_key=True, related_name="resultat")
	moyenne_generale = models.DecimalField(max_digits=4, decimal_places=2, editable=False)
	mention = models.CharField(choices=Mention.choices, max_length=5, editable=False)
	est_admis = models.BooleanField(default=False)
	date_proclamation = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _("Résultat final")

	def __str__(self):
		return f"Résultat {self.candidat.numero_candidat} : {self.mention}"
