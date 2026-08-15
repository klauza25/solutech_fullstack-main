import logging
import openpyxl
from datetime import datetime
from zipfile import BadZipFile
from openpyxl.utils.exceptions import InvalidFileException
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Eleve, LienFamille
from .serializers import EleveListSerializer, EleveDetailSerializer
from .permissions import EleveScopePermission
from ecoles.models import Classe

logger = logging.getLogger("apps.eleves")


class _RowValidationError(Exception):
    """Signal interne : au moins une ligne du fichier est invalide (rollback)"""


class EleveViewSet(viewsets.ModelViewSet):
    """CRUD Élèves avec scope par école/parent & import Excel (CDC §2.1, §4.5, §7.2)"""
    permission_classes = [permissions.IsAuthenticated, EleveScopePermission]
    
    def get_serializer_class(self):
        return EleveDetailSerializer if self.action == "retrieve" else EleveListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Eleve.objects.filter(is_active=True).select_related("ecole", "classe_actuelle").prefetch_related("parents")
        
        if user.is_superuser: return qs
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR"]:
            return qs.filter(ecole=user.ecole)
        if user.role == "PROFESSEUR":
            return qs.filter(ecole=user.ecole) if user.ecole else qs.none()
        if user.role == "PARENT":
            return qs.filter(parents=user)
        return qs.none()

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def import_excel(self, request):
        """Import massif depuis registre papier (format Excel .xlsx)"""
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "Fichier Excel requis"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.ecole_id is None:
            return Response(
                {"detail": "Aucun établissement rattaché à votre compte : import impossible"},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = {"created": 0, "updated": 0, "errors": []}

        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=2, values_only=True))  # Skip header
        except (InvalidFileException, BadZipFile, KeyError) as e:
            logger.warning("Import Excel : fichier illisible (%s)", type(e).__name__)
            return Response(
                {"detail": "Fichier Excel illisible ou corrompu (.xlsx attendu)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(rows) > 500:
            return Response({"detail": "Max 500 élèves par import"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        try:
            with transaction.atomic():
                for idx, row in enumerate(rows, start=2):
                    try:
                        self._import_row(row, request.user, results)
                    except (DjangoValidationError, IntegrityError, ValueError, TypeError, IndexError) as e:
                        # Erreur de données : collectée pour un retour ligne par ligne
                        results["errors"].append({"row": idx, "error": str(e)})

                if results["errors"]:
                    # Rollback explicite : aucun élève importé si une ligne est invalide
                    raise _RowValidationError()

        except _RowValidationError:
            logger.info(
                "Import Excel rejeté pour l'utilisateur %s : %d ligne(s) invalide(s)",
                request.user.id, len(results["errors"])
            )
            return Response(
                {"detail": "Erreurs de validation détectées. Aucune ligne importée.", "results": results},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError:
            # Panne serveur : ne pas la déguiser en erreur client, et garder la trace
            logger.exception("Import Excel échoué (base de données) pour l'utilisateur %s", request.user.id)
            return Response(
                {"detail": "Import impossible : erreur interne. Aucune donnée modifiée."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"message": "Import réussi", "results": results}, status=status.HTTP_200_OK)

    def _import_row(self, row, user, results):
        """Crée ou met à jour un élève depuis une ligne du fichier Excel"""
        matricule = str(row[0]).strip() if row[0] is not None else ""
        if not matricule:
            return

        # Savepoint : une erreur d'intégrité sur une ligne laisse la transaction
        # du batch utilisable pour continuer à collecter les autres erreurs
        with transaction.atomic():
            _, created = Eleve.objects.update_or_create(
                matricule_mepsa=matricule,
                defaults={
                    "nom": row[1], "prenom": row[2], "genre": row[3],
                    "date_naissance": row[4], "ecole": user.ecole
                }
            )
        if created:
            results["created"] += 1
        else:
            results["updated"] += 1