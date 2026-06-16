from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Genre(models.TextChoices):
    MASCULIN = "M", _("Masculin")
    FEMININ = "F", _("Féminin")

class StatutInscription(models.TextChoices):
    ACTIF = "ACTIF", _("Actif")
    TRANSFERE = "TRANSFERE", _("Transféré vers un autre établissement")
    EXCLU = "EXCLU", _("Exclu / Abandon scolaire")
    DIPLOME = "DIPLOME", _("Diplômé")

class TypeLienFamille(models.TextChoices):
    PERE = "PERE", _("Père")
    MERE = "MERE", _("Mère")
    TUTEUR = "TUTEUR", _("Tuteur légal")
    SIBLING = "SIBLING", _("Frère/Sœur majeur responsable")
    AUTRE = "AUTRE", _("Autre responsable désigné")

class Eleve(models.Model):
    """
    Profil élève — conforme CDC §2.1, §4.4, §7.2
    """
    matricule_mepsa = models.CharField(
        max_length=30, 
        unique=True, 
        help_text=_("Identifiant national MEPSA (ex: M2026-BZV-004521)")
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    genre = models.CharField(max_length=1, choices=Genre.choices)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100, blank=True)

    # Liens structurels
    ecole = models.ForeignKey(
        "ecoles.Ecole", 
        on_delete=models.PROTECT, 
        related_name="eleves",
        help_text=_("Établissement d'inscription")
    )
    classe_actuelle = models.ForeignKey(
        "ecoles.Classe", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="eleves_inscrits"
    )
    statut = models.CharField(
        max_length=20, 
        choices=StatutInscription.choices, 
        default=StatutInscription.ACTIF
    )

    # CDC §4.4 Gestion des redoublements
    est_redoublant = models.BooleanField(default=False, help_text=_("A déjà redoublé au moins une fois"))
    historique_redoublements = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Historique structuré : [{'classe': '6ème A', 'annee': '2024-2025', 'moyenne': 8.5}]")
    )

    # CDC §2.2 Santé & Préscolaire/Primaire
    groupe_sanguin = models.CharField(max_length=5, blank=True)
    vaccinations_a_jour = models.BooleanField(null=True, blank=True, help_text=_("Carnet vérifié (obligatoire CP1)"))
    notes_medicales = models.TextField(blank=True, help_text=_("Allergies, asthme, régime spécial, handicaps"))

    # Relations familiales (CDC §4.5)
    parents = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through="LienFamille", 
        related_name="enfants"
    )

    # Audit & Conformité
    is_active = models.BooleanField(default=True, help_text=_("Élève actif dans l'établissement"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Élève")
        verbose_name_plural = _("Élèves")
        ordering = ["nom", "prenom"]
        indexes = [
            models.Index(fields=["matricule_mepsa"]),
            models.Index(fields=["ecole", "statut"]),
            models.Index(fields=["genre", "classe_actuelle"]),  # Stats MEPSA genrées
        ]

    def __str__(self):
        return f"{self.nom.upper()} {self.prenom} ({self.matricule_mepsa})"


class LienFamille(models.Model):
    """Gestion réaliste des structures familiales congolaises (CDC §4.5)"""
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_lien = models.CharField(max_length=10, choices=TypeLienFamille.choices)
    est_responsable_financier = models.BooleanField(default=False, help_text=_("Prend en charge les frais scolaires"))
    est_contact_principal = models.BooleanField(default=True, help_text=_("Reçoit SMS/WhatsApp prioritaires"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("eleve", "parent")
        verbose_name = _("Lien familial")
        verbose_name_plural = _("Liens familiaux")

    def __str__(self):
        return f"{self.parent.get_full_name()} → {self.eleve.prenom} ({self.get_type_lien_display()})"