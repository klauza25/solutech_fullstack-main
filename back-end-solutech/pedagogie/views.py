from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.http import StreamingHttpResponse
import csv
from datetime import timedelta
from django.db.models import Count, Avg, Q, F, Value, CharField
from .models import Evaluation, Presence
from .serializers import EvaluationCreateSerializer, EvaluationReadSerializer, PresenceSerializer
from .permissions import PedagogyScopePermission
from rest_framework.exceptions import PermissionDenied


def check_school_scope(user, validated_data):
    """Interdit la saisie de notes/présences sur une classe ou un élève d'un autre établissement."""
    if user.is_superuser:
        return
    classe = validated_data.get("classe")
    eleve = validated_data.get("eleve")
    if user.ecole_id is None:
        raise PermissionDenied("Aucun établissement de rattachement pour cet utilisateur.")
    if classe is not None and classe.ecole_id != user.ecole_id:
        raise PermissionDenied("Classe hors de votre établissement.")
    if eleve is not None and eleve.ecole_id != user.ecole_id:
        raise PermissionDenied("Élève hors de votre établissement.")


def csv_safe(value):
    """Neutralise l'injection de formules (CSV/Excel) et les séparateurs."""
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        text = "'" + text
    return '"' + text.replace('"', '""') + '"'

class EvaluationViewSet(viewsets.ModelViewSet):
    """CRUD Évaluations avec filtrage contextuel & calcul moyennes"""
    permission_classes = [permissions.IsAuthenticated, PedagogyScopePermission]

    def get_serializer_class(self):
        return EvaluationCreateSerializer if self.action in ["create", "update", "partial_update"] else EvaluationReadSerializer

    def get_queryset(self):
        user = self.request.user
        # select_related évite les requêtes N+1 sur les FK
        qs = Evaluation.objects.select_related("eleve", "matiere", "classe__ecole")
        
        if user.is_superuser: return qs
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"]:
            return qs.filter(classe__ecole_id=user.ecole_id) if user.ecole_id else qs.none()
        if user.role == "PARENT":
            return qs.filter(eleve__parents=user)
        if user.role == "ELEVE":
            return qs.filter(eleve=user)
        return qs.none()

    def perform_create(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        # Pré-remplit la date si absente
        if not serializer.validated_data.get("date_eval"):
            serializer.save(date_eval=timezone.now().date())
        else:
            serializer.save()

    def perform_update(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        serializer.save()


class PresenceViewSet(viewsets.ModelViewSet):
    serializer_class = PresenceSerializer
    permission_classes = [permissions.IsAuthenticated, PedagogyScopePermission]

    def get_queryset(self):
        user = self.request.user
        qs = Presence.objects.select_related("eleve", "classe__ecole")
        
        if user.is_superuser: return qs
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"]:
            return qs.filter(classe__ecole_id=user.ecole_id) if user.ecole_id else qs.none()
        if user.role in ["PARENT", "ELEVE"]:
            return qs.filter(Q(eleve__parents=user) | Q(eleve=user))
        return qs.none()

    def perform_create(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        serializer.save(recorded_by=self.request.user)

    def perform_update(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        serializer.save()

    @action(detail=False, methods=["get"], url_path="dropout-alerts")
    def dropout_alerts(self, request):
        """Alerte précoce décrochage (CDC §4.1) — Réservé Direction"""
        if not request.user.is_superuser and request.user.role not in ["ADMIN", "DIRECTEUR", "CENSEUR"]:
            return Response({"detail": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)

        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        current_trim = 1  # À dynamiser via config calendrier scolaire

        # 1️⃣ Absences ≥ 3 sur 30 jours
        abs_alerts = Presence.objects.filter(
            classe__ecole=request.user.ecole,
            date__gte=thirty_days_ago,
            statut="ABS"
        ).values("eleve__id", "eleve__nom", "eleve__prenom", "eleve__genre").annotate(
            total_abs=Count("id")
        ).filter(total_abs__gte=3).annotate(
            alerte_type=Value("Absences répétées", output_field=CharField())
        ).values("eleve__id", "eleve__nom", "eleve__prenom", "eleve__genre", "alerte_type")

        # 2️⃣ Moyenne trimestrielle < 8/20
        grade_alerts = Evaluation.objects.filter(
            classe__ecole=request.user.ecole,
            trimestre=current_trim
        ).values("eleve__id", "eleve__nom", "eleve__prenom", "eleve__genre").annotate(
            avg_note=Avg("note_sur_20"),
            alerte_type=Value("Moyenne < 8/20", output_field=CharField())
        ).filter(avg_note__lt=8.0)

        # Fusion & formatage léger
        alerts = list(abs_alerts) + list(grade_alerts)
        return Response({"count": len(alerts), "alerts": alerts}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        """Export CSV léger pour rapports MEPSA / directeurs (CDC §3.2)"""
        if not request.user.is_superuser and request.user.role not in ["ADMIN", "DIRECTEUR", "CENSEUR"]:
            return Response({"detail": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)

        qs = self.get_queryset()
        def stream_data():
            # BOM UTF-8 pour compatibilité Excel
            yield "\ufeffMatricule,Nom,Prenom,Classe,Date,Statut\n"
            for p in qs.iterator():
                yield ",".join(csv_safe(v) for v in (
                    p.eleve.matricule_mepsa, p.eleve.nom, p.eleve.prenom,
                    p.classe.nom, p.date, p.get_statut_display(),
                )) + "\n"

        response = StreamingHttpResponse(stream_data(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="presences_export.csv"'
        return response
