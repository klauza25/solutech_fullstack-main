from django.db import models
from django.utils.translation import gettext_lazy as _
from eleves.models import Eleve
from ecoles.models import Classe

class Trimestre(models.IntegerChoices):
    TRIMESTRE_1 = 1, _("1er Trimestre (Septembre → Décembre)")
    TRIMESTRE_2 = 2, _("2ème Trimestre (Janvier → Mars)")
    TRIMESTRE_3 = 3, _("3ème Trimestre (Avril → Juin/Juillet)")

class TypeEvaluation(models.TextChoices):
    INTERROGATION = "INT", _("Interrogation / Contrôle continu")
    DEVOIR = "DEV", _("Devoir surveillé")
    EXAMEN = "EXA", _("Examen de fin de trimestre")
    TP = "TP", _("Travaux Pratiques (Enseignement technique)")

class StatutPresence(models.TextChoices):
    PRESENT = "PRE", _("Présent")
    ABSENT = "ABS", _("Absent non justifié")
    EXCUSE = "EXC", _("Absent justifié (certificat médical, etc.)")
    RETARD = "RET", _("Retard")

class Matiere(models.Model):
    """Matières officielles MEPSA par cycle"""
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text=_("Code MEPSA (ex: MATH6, FR3, HIST4)"))
    coefficient_defaut = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    est_obligatoire = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Matière")
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} ({self.code})"

class Evaluation(models.Model):
    """Note individuelle conforme CDC §2.1 & §2.5"""
    eleve = models.ForeignKey(Eleve, on_delete=models.PROTECT, related_name="evaluations")
    matiere = models.ForeignKey(Matiere, on_delete=models.PROTECT)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name="evaluations")
    trimestre = models.PositiveSmallIntegerField(choices=Trimestre.choices)
    type_eval = models.CharField(max_length=3, choices=TypeEvaluation.choices)
    coefficient = models.DecimalField(max_digits=3, decimal_places=1)
    note_sur_20 = models.DecimalField(max_digits=4, decimal_places=2, help_text=_("Note sur 20, au centième"))
    date_eval = models.DateField()
    est_validee = models.BooleanField(default=False, help_text=_("Verrouillée après conseil de classe"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Évaluation")
        constraints = [
            models.UniqueConstraint(
                fields=["eleve", "matiere", "trimestre", "type_eval"],
                name="unique_eval_par_eleve_matiere_trim_type"
            )
        ]
        ordering = ["-date_eval"]

    def __str__(self):
        return f"{self.eleve.prenom} - {self.matiere.nom} : {self.note_sur_20}/20"

class Presence(models.Model):
    """Suivi quotidien des présences (CDC §4.1 Alerte décrochage)"""
    eleve = models.ForeignKey(Eleve, on_delete=models.PROTECT)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    date = models.DateField()
    trimestre = models.PositiveSmallIntegerField(choices=Trimestre.choices)
    statut = models.CharField(max_length=3, choices=StatutPresence.choices)
    justification = models.TextField(blank=True, null=True, help_text=_("Motif ou référence certificat"))
    recorded_by = models.ForeignKey("comptes.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Présence")
        constraints = [
            models.UniqueConstraint(
                fields=["eleve", "date"],
                name="unique_presence_par_jour"
            )
        ]
        indexes = [
            models.Index(fields=["trimestre", "statut"]),
            models.Index(fields=["eleve", "trimestre"]),
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.eleve.prenom} | {self.date} → {self.get_statut_display()}"
