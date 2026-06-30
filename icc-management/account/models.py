from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    """Les départements de l'église (Louange, Protocole, etc.)"""
    name = models.CharField("Nom du département", max_length=100, unique=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    """Utilisateur personnalisé pour l'église"""
    ROLE_CHOICES = (
        ('admin', 'Administrateur Général'),
        ('chef', 'Chef de Département'),
        ('serviteur', 'Serviteur'),
    )
    
    # Champs de l'église
    nom = models.CharField("Nom", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    role = models.CharField("Rôle", max_length=10, choices=ROLE_CHOICES, default='serviteur')
    departement = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Département",
        related_name="members"
    )
    
    # Informations personnelles
    telephone = models.CharField("Téléphone", max_length=20, blank=True, null=True)
    adresse = models.TextField("Adresse", blank=True, null=True)
    profession = models.CharField("Profession (Statut)", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_role_display()})"