import json
import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

logger = logging.getLogger("apps.sync")

def log_sync_failure(device_id: str, user_id: int, error_type: str, details: str = ""):
    """Log structuré JSON pour monitoring admin (conforme CDC §7.2)"""
    logger.warning(
        json.dumps({
            "event": "SYNC_FAILURE",
            "device_id": device_id,
            "user_id": user_id,
            "error_type": error_type,
            "details": details,
            "timestamp": timezone.now().isoformat()
        })
    )

def validate_delta_window(last_sync_str: str | None) -> timezone.datetime:
    """Valide et nettoie la fenêtre de delta sync.

    Un paramètre absent donne un fallback de 7 jours ; un paramètre mal formé est
    une erreur client explicite (400) — le silence ferait croire au client que sa
    fenêtre a été respectée alors qu'un delta différent est renvoyé.
    """
    if not last_sync_str:
        return timezone.now() - timedelta(days=7)  # Fallback : 7 jours

    try:
        last_sync = timezone.datetime.fromisoformat(last_sync_str.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError) as e:
        raise ValidationError({
            "last_sync": "Format de date invalide. Attendu : ISO 8601 (ex: 2026-05-10T14:00:00Z)."
        }) from e

    # Une date naïve est interprétée dans le fuseau courant (sinon la comparaison
    # ci-dessous lèverait un TypeError)
    if timezone.is_naive(last_sync):
        last_sync = timezone.make_aware(last_sync)

    # Empêche les requêtes malveillantes ou décalées
    return max(last_sync, timezone.now() - timedelta(days=30))