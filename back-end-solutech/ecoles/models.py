from django.db import models
from django.utils.translation import gettext_lazy as _

class SchoolType(models.TextChoices):
    """Types d'établissements selon la réglementation MEPSA 🇨🇬"""
    PUBLIC = "PUBLIC", _("Établissement public (État)")
    PRIVE_CONV_I = "PRIVE_CONV_I", _("Privé conventionné Type I — subventionné")
    PRIVE_CONV_II = "PRIVE_CONV_II", _("Privé conventionné Type II — partiellement subventionné")
    PRIVE_NON_CONV = "PRIVE_NON_CONV", _("Privé non conventionné")
    CONFESSIONNEL = "CONFESSIONNEL", _("Établissement confessionnel")
    TECHNIQUE = "TECHNIQUE", _("Établissement technique / professionnel (LTP/CFP)")

class EducationLevel(models.TextChoices):
    """Cycles éducatifs officiels — République du Congo"""
    PRESOLAIRE = "PRESOLAIRE", _("Préscolaire (3-5 ans)")
    PRIMAIRE = "PRIMAIRE", _("Primaire (CP1→CM2)")
    COLLEGE = "COLLEGE", _("Collège d'Enseignement Général — CEG (6ème→3ème)")
    LYCEE = "LYCEE", _("Lycée d'Enseignement Général — LEG (2nde→Terminale)")
    TECHNIQUE_PRO = "TECHNIQUE_PRO", _("Enseignement technique / professionnel")

class Ecole(models.Model):
    """
    Établissement scolaire — conforme nomenclature MEPSA
    """
    nom = models.CharField(max_length=200, help_text=_("Nom officiel de l'établissement"))
    code_mepsa = models.CharField(
        max_length=50, 
        unique=True, 
        help_text=_("Code d'identification MEPSA (ex: BZV-CEG-001, PNR-LEG-012)")
    )
    type = models.CharField(
        max_length=30, 
        choices=SchoolType.choices, 
        default=SchoolType.PUBLIC,
        help_text=_("Catégorie juridique et financière de l'établissement")
    )
    cycles = models.CharField(
        max_length=100,
        help_text=_("Cycles enseignés, séparés par des virgules (ex: 'PRIMAIRE,COLLEGE')")
    )
    
    # Localisation
    region = models.CharField(max_length=50, help_text=_("Région (Brazzaville, Pointe-Noire, Niari, etc.)"))
    district = models.CharField(max_length=100, blank=True, help_text=_("District / Arrondissement"))
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    # Direction (FK différée vers comptes.User à l'étape 3)
    # directeur = models.ForeignKey("comptes.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="ecoles_dirigees")
    
    # Meta & Audit
    is_active = models.BooleanField(default=True, help_text=_("Établissement opérationnel"))
    date_ouverture = models.DateField(null=True, blank=True, help_text=_("Date de création officielle"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Établissement scolaire")
        verbose_name_plural = _("Établissements scolaires")
        ordering = ["region", "nom"]
        indexes = [
            models.Index(fields=["code_mepsa"]),
            models.Index(fields=["type", "is_active"]),
            models.Index(fields=["region"]),
        ]
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_display()}) — {self.region}"
    
    

class ClasseNiveau(models.TextChoices):
    """Niveaux officiels — Nomenclature MEPSA République du Congo 🇨🇬"""
    PRESOL_PS = "PS", _("Préscolaire - Petite Section")
    PRESOL_MS = "MS", _("Préscolaire - Moyenne Section")
    PRESOL_GS = "GS", _("Préscolaire - Grande Section")
    
    PRIMAIRE_CP1 = "CP1", _("CP1")
    PRIMAIRE_CP2 = "CP2", _("CP2")
    PRIMAIRE_CE1 = "CE1", _("CE1")
    PRIMAIRE_CE2 = "CE2", _("CE2")
    PRIMAIRE_CM1 = "CM1", _("CM1")
    PRIMAIRE_CM2 = "CM2", _("CM2")
    
    COLLEGE_6EME = "6EME", _("6ème")
    COLLEGE_5EME = "5EME", _("5ème")
    COLLEGE_4EME = "4EME", _("4ème")
    COLLEGE_3EME = "3EME", _("3ème")
    
    LYCEE_2NDE = "2NDE", _("2nde")
    LYCEE_1ERE = "1ERE", _("1ère")
    LYCEE_TLE = "TLE", _("Terminale")

class Classe(models.Model):
    """
    Division pédagogique concrète au sein d'un établissement.
    Ex: "6ème A", "CM2 1", "Terminale S"
    """
    nom = models.CharField(
        max_length=50, 
        help_text=_("Nom usuel de la classe (ex: 6ème A, CM2 1, Terminale L)")
    )
    niveau = models.CharField(
        max_length=10, 
        choices=ClasseNiveau.choices,
        help_text=_("Niveau officiel MEPSA")
    )
    ecole = models.ForeignKey(
        "ecoles.Ecole", 
        on_delete=models.CASCADE, 
        related_name="classes",
        help_text=_("Établissement auquel appartient cette classe")
    )
    capacite_max = models.PositiveIntegerField(
        default=45, 
        help_text=_("Effectif maximum recommandé par la circulaire MEPSA")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # FK différées (à décommenter après création des apps correspondantes)
    # prof_principal = models.ForeignKey(
    #     "comptes.User", on_delete=models.SET_NULL, null=True, blank=True,
    #     related_name="classes_dirigees", limit_choices_to={"role": "PROFESSEUR"}
    # )
    
    class Meta:
        verbose_name = _("Classe")
        verbose_name_plural = _("Classes")
        ordering = ["ecole__nom", "niveau", "nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "ecole"], 
                name="unique_classe_par_ecole"
            )
        ]
        indexes = [
            models.Index(fields=["niveau", "is_active"]),
            models.Index(fields=["ecole", "is_active"]),
        ]
    
    def __str__(self):
        return f"{self.nom} — {self.ecole.nom} ({self.get_niveau_display()})"