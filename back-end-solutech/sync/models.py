import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class OperationType(models.TextChoices):
    CREATE = "CREATE", _("Création")
    UPDATE = "UPDATE", _("Modification")
    DELETE = "DELETE", _("Suppression")

class SyncStatus(models.TextChoices):
    PENDING = "PENDING", _("En attente de traitement")
    PROCESSED = "PROCESSED", _("Traitée avec succès")
    CONFLICT = "CONFLICT", _("Conflit détecté (server_wins)")
    ERROR = "ERROR", _("Erreur de validation")

class SyncQueue(models.Model):
    """
    File d'attente des opérations offline.
    Représente une action locale (ex: saisie de note hors ligne) 
    qui sera synchronisée au serveur dès connexion.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(
        max_length=100, 
        help_text=_("ID unique de l'appareil client (UUID généré côté PWA/mobile)")
    )
    client_operation_id = models.UUIDField(
        unique=True, 
        help_text=_("ID idempotent généré par le client pour éviter les doublons en cas de retry réseau")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="sync_operations"
    )
    operation_type = models.CharField(choices=OperationType.choices, max_length=10)
    model_name = models.CharField(
        max_length=50, 
        help_text=_("Nom du modèle Django cible (ex: 'eleves.Eleve', 'pedagogie.Note')")
    )
    payload = models.JSONField(
        help_text=_("Données brutes de l'opération (JSON sérialisé)")
    )
    status = models.CharField(
        choices=SyncStatus.choices, 
        default=SyncStatus.PENDING,
        db_index=True
    )
    conflict_details = models.JSONField(null=True, blank=True, help_text=_("Détails du conflit si server_wins"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Opération de synchronisation")
        verbose_name_plural = _("File de synchronisation")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device_id", "status"]),
            models.Index(fields=["client_operation_id"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.operation_type}] {self.model_name} — {self.status} ({self.device_id})"

class SyncConflictLog(models.Model):
    """Journal d'audit des conflits résolus (conformité CDC §7.1)"""
    sync_op = models.ForeignKey(SyncQueue, on_delete=models.CASCADE, related_name="conflicts")
    local_version = models.JSONField(help_text=_("Données envoyées par le client"))
    server_version = models.JSONField(help_text=_("Données actuelles en base"))
    resolution = models.CharField(max_length=20, default="server_wins")
    created_at = models.DateTimeField(auto_now_add=True)