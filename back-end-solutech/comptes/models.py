from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _



class UserManager(BaseUserManager):
    """Manager personnalisé pour garantir la création cohérente des utilisateurs"""
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('Le nom d\'utilisateur est obligatoire'))
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # 🔐 Hachage automatique sécurisé
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """Modèle utilisateur conforme à la nomenclature MEPSA 🇨🇬"""
    
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur Solutech')
        DIRECTEUR = 'DIRECTEUR', _('Directeur / Proviseur / Censeur')
        PROFESSEUR = 'PROFESSEUR', _('Professeur / Instituteur')
        ELEVE = 'ELEVE', _('Élève')
        PARENT = 'PARENT', _('Parent / Tuteur')
        INSPECTEUR = 'INSPECTEUR', _('Inspecteur MEPSA')

    objects = UserManager()
    
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.ELEVE,
        help_text=_('Rôle dans l\'écosystème éducatif')
    )
    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Numéro au format +242 ou 06... (prépa SMS/Mobile Money)')
    )    
    # 🔗 Lien vers l'établissement (nul pour le SuperAdmin central)
    ecole = models.ForeignKey(
        "ecoles.Ecole", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="utilisateurs",
        help_text=_("Établissement de rattachement principal")
    )
    # school = models.ForeignKey('schools.School', on_delete=models.SET_NULL, null=True, blank=True)  # Phase 2

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"