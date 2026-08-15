import logging
import openpyxl
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Eleve
from .serializers import EleveListSerializer, EleveDetailSerializer
from .permissions import EleveScopePermission

logger = logging.getLogger("apps.eleves")

class EleveViewSet(viewsets.ModelViewSet):
    """CRUD Élèves avec scope par école/parent & import Excel (CDC §2.1, §4.5, §7.2)"""
    permission_classes = [permissions.IsAuthenticated, EleveScopePermission]
    
    def get_serializer_class(self):
        if self.action in ("retrieve", "create", "update", "partial_update"):
            return EleveDetailSerializer
        return EleveListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Eleve.objects.filter(is_active=True).select_related("ecole", "classe_actuelle").prefetch_related("parents")
        
        if user.is_superuser: return qs
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"]:
            return qs.filter(ecole_id=user.ecole_id) if user.ecole_id else qs.none()
        if user.role == "PARENT":
            return qs.filter(parents=user)
        return qs.none()

    def perform_create(self, serializer):
        # L'école n'est jamais acceptée depuis le client (voir serializer) : elle
        # est déduite de l'utilisateur pour interdire toute création inter-établissement.
        if self.request.user.is_superuser:
            serializer.save()
            return
        if not self.request.user.ecole_id:
            raise ValidationError("Aucun établissement de rattachement pour cet utilisateur.")
        serializer.save(ecole=self.request.user.ecole)

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def import_excel(self, request):
        """Import massif depuis registre papier (format Excel .xlsx)"""
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "Fichier Excel requis"}, status=status.HTTP_400_BAD_REQUEST)

        ecole = request.user.ecole
        if ecole is None:
            return Response(
                {"detail": "Aucun établissement de rattachement pour cet utilisateur."},
                status=status.HTTP_403_FORBIDDEN,
            )

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

                        # Scope établissement : un import ne peut jamais écraser la fiche
                        # d'un élève inscrit dans une autre école.
                        conflit = Eleve.objects.filter(matricule_mepsa=matricule).exclude(ecole=ecole).exists()
                        if conflit:
                            results["errors"].append({
                                "row": idx,
                                "error": "Matricule déjà utilisé dans un autre établissement",
                            })
                            continue

                        eleve, created = Eleve.objects.update_or_create(
                            matricule_mepsa=matricule,
                            ecole=ecole,
                            defaults={
                                "nom": row[1], "prenom": row[2], "genre": row[3],
                                "date_naissance": row[4],
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
            return Response(
                {"detail": "Import impossible : fichier invalide ou données rejetées.", "results": results},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Import réussi", "results": results}, status=status.HTTP_200_OK)