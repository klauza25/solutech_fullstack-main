# === IMPORTS STANDARD ===
import json
import logging
# === IMPORTS DJANGO ===
from django.apps import apps
from django.db import IntegrityError, transaction
from django.utils import timezone
# === IMPORTS DRF ===
from rest_framework.response import Response
from rest_framework import status
from common.views import ThrottledAPIView
from .utils import validate_delta_window, log_sync_failure
# === IMPORTS LOCAUX ===
from .models import SyncQueue, OperationType, SyncStatus, SyncConflictLog
from .serializers import SyncBatchInputSerializer, SyncBatchResponseSerializer

logger = logging.getLogger("apps.sync")

# Whitelist stricte des modèles synchronisables (CDC §3.1)
ALLOWED_SYNC_MODELS = {"ecoles.Ecole", "ecoles.Classe"}  # Étendre progressivement


class SyncModelNotAllowed(Exception):
    """Opération portant sur un modèle hors whitelist : erreur client (400)"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(f"Modèle non autorisé : {model_name}")


class SyncPushView(ThrottledAPIView):
    """Endpoint POST /api/sync/push/ — Traitement batch idempotent"""

    def post(self, request):
        input_data = SyncBatchInputSerializer(data=request.data)
        input_data.is_valid(raise_exception=True)

        operations = input_data.validated_data["operations"]
        if len(operations) > 50:
            return Response(
                {"detail": "Batch trop volumineux. Max 50 opérations."}, 
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        device_id = input_data.validated_data["device_id"]
        report = {"processed": 0, "conflicts": 0, "errors": 0, "details": []}

        try:
            with transaction.atomic():  # 🔒 Atomicité totale du batch
                for op_data in operations:
                    self._process_operation(op_data, device_id, request.user, report)

        except SyncModelNotAllowed as e:
            # Erreur imputable au client : la distinguer d'une panne serveur
            log_sync_failure(device_id, request.user.id, "MODEL_NOT_ALLOWED", e.model_name)
            return Response(
                {"detail": str(e), "allowed_models": sorted(ALLOWED_SYNC_MODELS)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # ⚠️ Ne jamais logger le payload complet (données sensibles)
            log_sync_failure(device_id, request.user.id, type(e).__name__)
            logger.exception("Sync batch failed for user %s", request.user.id)
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

    def _process_operation(self, op_data, device_id, user, report):
        """Traite une opération du batch et enrichit le rapport.

        Lève SyncModelNotAllowed (400) ou toute autre exception (500) : dans les
        deux cas la transaction du batch est annulée par l'appelant.
        """
        client_id = op_data["client_operation_id"]
        model_name = op_data["model_name"]

        # ✅ Idempotence : ignorer si déjà traité
        if SyncQueue.objects.filter(
            client_operation_id=client_id, 
            status=SyncStatus.PROCESSED
        ).exists():
            report["details"].append({
                "client_operation_id": str(client_id), 
                "status": "ALREADY_PROCESSED"
            })
            return

        # ✅ Validation du modèle cible
        if model_name not in ALLOWED_SYNC_MODELS:
            raise SyncModelNotAllowed(model_name)

        # ✅ Création de l'entrée en file d'attente
        try:
            # Savepoint : une collision d'unicité ne doit pas invalider le batch
            with transaction.atomic():
                queue_entry = SyncQueue.objects.create(
                    device_id=device_id,
                    client_operation_id=client_id,
                    user=user,
                    operation_type=op_data["operation_type"],
                    model_name=model_name,
                    payload=op_data["payload"],
                    status=SyncStatus.PENDING
                )
        except IntegrityError:
            # client_operation_id est unique : un retry concurrent a déjà inséré la ligne
            log_sync_failure(device_id, user.id, "DUPLICATE_OPERATION", str(client_id))
            report["details"].append({
                "client_operation_id": str(client_id),
                "status": "ALREADY_PROCESSED",
                "message": "Opération déjà enregistrée (retry concurrent)"
            })
            return

        # 🔧 Traitement simulé (logique métier réelle à implémenter par modèle en Phase 4)
        queue_entry.status = SyncStatus.PROCESSED
        queue_entry.processed_at = timezone.now()
        queue_entry.save(update_fields=["status", "processed_at"])

        report["processed"] += 1
        report["details"].append({
            "client_operation_id": str(client_id), 
            "status": "PROCESSED"
        })


class SyncStatusView(ThrottledAPIView):
    """
    GET /api/sync/status/
    Retourne l'état de synchronisation des opérations du client connecté.
    Réponse optimisée : uniquement les IDs + statuts (pas de payloads).
    """

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
    
    

class SyncPingView(ThrottledAPIView):
    """
    GET /api/sync/ping/
    Mesure la latence réseau. Utilisé par la PWA pour basculer online/offline.
    """
    permission_classes = []  # Public, sans auth

    def get(self, request):
        return Response({
            "status": "ok",
            "server_time": timezone.now().isoformat(),
            "timezone": timezone.get_current_timezone_name()
        }, status=status.HTTP_200_OK)

class SyncDeltaView(ThrottledAPIView):
    """
    GET /api/sync/delta/?last_sync=2026-05-10T14:00:00Z
    Retourne uniquement les modifications récentes (CDC §3.2 Faible bande passante)
    """

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