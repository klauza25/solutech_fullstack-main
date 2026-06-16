# === IMPORTS STANDARD ===
import json
import logging
# === IMPORTS DJANGO ===
from django.apps import apps
from django.db import transaction
from django.utils import timezone
# === IMPORTS DRF ===
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.throttling import UserRateThrottle
from .utils import validate_delta_window, log_sync_failure
# === IMPORTS LOCAUX ===
from .models import SyncQueue, OperationType, SyncStatus, SyncConflictLog
from .serializers import SyncBatchInputSerializer, SyncBatchResponseSerializer

logger = logging.getLogger("apps.sync")

# Whitelist stricte des modèles synchronisables (CDC §3.1)
ALLOWED_SYNC_MODELS = {"ecoles.Ecole", "ecoles.Classe"}  # Étendre progressivement


class SyncPushView(APIView):
    """Endpoint POST /api/sync/push/ — Traitement batch idempotent"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        input_data = SyncBatchInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)

        operations = input_data.validated_data["operations"]
        if len(operations) > 50:
            return Response(
                {"detail": "Batch trop volumineux. Max 50 opérations."}, 
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        report = {"processed": 0, "conflicts": 0, "errors": 0, "details": []}

        try:
            with transaction.atomic():  # 🔒 Atomicité totale du batch
                for op_data in operations:
                    client_id = op_data["client_operation_id"]
                    model_name = op_data["model_name"]
                    op_type = op_data["operation_type"]
                    payload = op_data["payload"]

                    # ✅ Idempotence : ignorer si déjà traité
                    if SyncQueue.objects.filter(
                        client_operation_id=client_id, 
                        status=SyncStatus.PROCESSED
                    ).exists():
                        report["details"].append({
                            "client_operation_id": str(client_id), 
                            "status": "ALREADY_PROCESSED"
                        })
                        continue

                    # ✅ Validation du modèle cible
                    if model_name not in ALLOWED_SYNC_MODELS:
                        raise ValueError(f"Modèle non autorisé : {model_name}")

                    # ✅ Création de l'entrée en file d'attente
                    queue_entry = SyncQueue.objects.create(
                        device_id=input_data.validated_data["device_id"],
                        client_operation_id=client_id,
                        user=request.user,
                        operation_type=op_type,
                        model_name=model_name,
                        payload=payload,
                        status=SyncStatus.PENDING
                    )

                    # 🔧 Traitement simulé (logique métier réelle à implémenter par modèle en Phase 4)
                    queue_entry.status = SyncStatus.PROCESSED
                    queue_entry.processed_at = timezone.now()
                    queue_entry.save(update_fields=["status", "processed_at"])

                    report["processed"] += 1
                    report["details"].append({
                        "client_operation_id": str(client_id), 
                        "status": "PROCESSED"
                    })

        except Exception as e:
            # ⚠️ Ne jamais logger le payload complet (données sensibles)
            logger.error(f"Sync batch failed for user {request.user.id}: {type(e).__name__}")
            # transaction.atomic() assure le rollback automatique
            return Response(
                {"detail": "Échec de synchronisation. Données non altérées."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Enrichir le rapport
        report["server_time"] = timezone.now().isoformat()
        return Response(
            SyncBatchResponseSerializer(report).data, 
            status=status.HTTP_200_OK
        )


class SyncStatusView(APIView):
    """
    GET /api/sync/status/
    Retourne l'état de synchronisation des opérations du client connecté.
    Réponse optimisée : uniquement les IDs + statuts (pas de payloads).
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        # Filtrage strict : l'utilisateur ne voit QUE ses propres opérations
        pending_ops = SyncQueue.objects.filter(
            user=request.user,
            status=SyncStatus.PENDING
        ).values("client_operation_id", "operation_type", "model_name", "created_at")
        
        processed_ops = SyncQueue.objects.filter(
            user=request.user,
            status=SyncStatus.PROCESSED,
            processed_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).values("client_operation_id", "status", "processed_at")
        
        conflicts = SyncQueue.objects.filter(
            user=request.user,
            status=SyncStatus.CONFLICT
        ).values("client_operation_id", "conflict_details")

        # 🔍 Gestion sécurisée de last_sync (peut être None)
        last_sync = getattr(request.user, "last_sync", None)
        last_sync_iso = last_sync.isoformat() if last_sync else None

        response_data = {
            "device_id": request.META.get("HTTP_X_DEVICE_ID", "unknown"),
            "pending_count": pending_ops.count(),
            "processed_count": processed_ops.count(),
            "conflict_count": conflicts.count(),
            "last_sync": last_sync_iso,
            "server_time": timezone.now().isoformat(),
            "operations": {
                "pending": list(pending_ops),
                "processed": list(processed_ops),
                "conflicts": list(conflicts)
            }
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        # Headers PWA cache optimisés (CDC §3.2)
        response["Cache-Control"] = "no-cache, must-revalidate"
        # ETag simple basé sur le hash du contenu (suffisant pour PWA)
        response["ETag"] = f'"{abs(hash(json.dumps(response_data, sort_keys=True)))}"'
        response["X-Sync-Version"] = "2.0"
        return response
    
    

class SyncPingView(APIView):
    """
    GET /api/sync/ping/
    Mesure la latence réseau. Utilisé par la PWA pour basculer online/offline.
    """
    permission_classes = []  # Public, sans auth
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        return Response({
            "status": "ok",
            "server_time": timezone.now().isoformat(),
            "timezone": timezone.get_current_timezone_name()
        }, status=status.HTTP_200_OK)

class SyncDeltaView(APIView):
    """
    GET /api/sync/delta/?last_sync=2026-05-10T14:00:00Z
    Retourne uniquement les modifications récentes (CDC §3.2 Faible bande passante)
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        last_sync = validate_delta_window(request.query_params.get("last_sync"))
        
        # Exemple : delta pour les écoles (à étendre aux autres modèles métier)
        from ecoles.models import Ecole, Classe
        
        updated_ecoles = Ecole.objects.filter(
            updated_at__gte=last_sync, 
            is_active=True
        ).values("id", "nom", "code_mepsa", "updated_at")
        
        updated_classes = Classe.objects.filter(
            updated_at__gte=last_sync,
            is_active=True
        ).values("id", "nom", "niveau", "ecole_id", "updated_at")

        # Marquer la nouvelle synchronisation réussie
        request.user.last_sync = timezone.now()
        request.user.save(update_fields=["last_sync"])

        return Response({
            "delta_since": last_sync.isoformat(),
            "server_time": timezone.now().isoformat(),
            "modified": {
                "ecoles": list(updated_ecoles),
                "classes": list(updated_classes)
            }
        }, status=status.HTTP_200_OK)