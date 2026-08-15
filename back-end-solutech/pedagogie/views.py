from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Value, CharField
from common.exports import stream_csv_response
from common.permissions import IsDirection
from common.scoping import RoleScopedQuerysetMixin
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


class PedagogieScopeMixin(RoleScopedQuerysetMixin):
    """Scope commun aux modèles pédagogiques rattachés à une classe et un élève."""
    scope_ecole_path = "classe__ecole"
    scope_parent_path = "eleve__parents"
    scope_eleve_path = "eleve"
    permission_classes = [permissions.IsAuthenticated, PedagogyScopePermission]


class EvaluationViewSet(PedagogieScopeMixin, viewsets.ModelViewSet):
    """CRUD Évaluations avec filtrage contextuel & calcul moyennes"""
    # select_related évite les requêtes N+1 sur les FK
    base_queryset = Evaluation.objects.select_related("eleve", "matiere", "classe__ecole")

    def get_serializer_class(self):
        return EvaluationCreateSerializer if self.action in ["create", "update", "partial_update"] else EvaluationReadSerializer

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


class PresenceViewSet(PedagogieScopeMixin, viewsets.ModelViewSet):
    serializer_class = PresenceSerializer
    base_queryset = Presence.objects.select_related("eleve", "classe__ecole")

    def perform_create(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        serializer.save(recorded_by=self.request.user)

    def perform_update(self, serializer):
        check_school_scope(self.request.user, serializer.validated_data)
        serializer.save()

    @action(
        detail=False,
        methods=["get"],
        url_path="dropout-alerts",
        permission_classes=[permissions.IsAuthenticated, IsDirection],
    )
    def dropout_alerts(self, request):
        """Alerte précoce décrochage (CDC §4.1) — Réservé Direction"""
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        current_trim = 1  # À dynamiser via config calendrier scolaire

        eleve_fields = ["eleve__id", "eleve__nom", "eleve__prenom", "eleve__genre"]

        # 1️⃣ Absences ≥ 3 sur 30 jours
        abs_alerts = Presence.objects.filter(
            classe__ecole=request.user.ecole,
            date__gte=thirty_days_ago,
            statut="ABS"
        ).values(*eleve_fields).annotate(
            total_abs=Count("id")
        ).filter(total_abs__gte=3).annotate(
            alerte_type=Value("Absences répétées", output_field=CharField())
        ).values(*eleve_fields, "alerte_type")

        # 2️⃣ Moyenne trimestrielle < 8/20
        grade_alerts = Evaluation.objects.filter(
            classe__ecole=request.user.ecole,
            trimestre=current_trim
        ).values(*eleve_fields).annotate(
            avg_note=Avg("note_sur_20"),
            alerte_type=Value("Moyenne < 8/20", output_field=CharField())
        ).filter(avg_note__lt=8.0)

        # Fusion & formatage léger
        alerts = list(abs_alerts) + list(grade_alerts)
        return Response({"count": len(alerts), "alerts": alerts}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="export-csv",
        permission_classes=[permissions.IsAuthenticated, IsDirection],
    )
    def export_csv(self, request):
        """Export CSV léger pour rapports MEPSA / directeurs (CDC §3.2)"""
        rows = (
            (
                p.eleve.matricule_mepsa,
                p.eleve.nom,
                p.eleve.prenom,
                p.classe.nom,
                p.date,
                p.get_statut_display(),
            )
            for p in self.get_queryset().iterator()
        )
        return stream_csv_response(
            "presences_export.csv",
            ["Matricule", "Nom", "Prenom", "Classe", "Date", "Statut"],
            rows,
        )
