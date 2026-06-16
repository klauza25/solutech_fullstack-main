import json
import logging
from django.utils import timezone
from datetime import timedelta

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
    """Valide et nettoie la fenêtre de delta sync"""
    if not last_sync_str:
        return timezone.now() - timedelta(days=7)  # Fallback : 7 jours
    
    try:
        last_sync = timezone.datetime.fromisoformat(last_sync_str.replace("Z", "+00:00"))
        # Empêche les requêtes malveillantes ou décalées
        return max(last_sync, timezone.now() - timedelta(days=30))
    except (ValueError, TypeError):
        return timezone.now() - timedelta(days=7)