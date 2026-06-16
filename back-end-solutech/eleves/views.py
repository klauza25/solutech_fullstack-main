import logging
import openpyxl
from datetime import datetime
from django.db import transaction
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

        results = {"created": 0, "updated": 0, "errors": []}
        
        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=2, values_only=True))  # Skip header
            if len(rows) > 500:
                return Response({"detail": "Max 500 élèves par import"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

            with transaction.atomic():
                for idx, row in enumerate(rows, start=2):
                    try:
                        matricule = str(row[0]).strip()
                        if not matricule: continue
                        
                        eleve, created = Eleve.objects.update_or_create(
                            matricule_mepsa=matricule,
                            defaults={
                                "nom": row[1], "prenom": row[2], "genre": row[3],
                                "date_naissance": row[4], "ecole": request.user.ecole
                            }
                        )
                        if created: results["created"] += 1
                        else: results["updated"] += 1
                    except Exception as e:
                        results["errors"].append({"row": idx, "error": str(e)})
                
                if results["errors"]:
                    raise Exception("Erreurs de validation détectées")

        except Exception as e:
            logger.error(f"Import Excel échoué: {e}")
            return Response({"detail": str(e), "results": results}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Import réussi", "results": results}, status=status.HTTP_200_OK)