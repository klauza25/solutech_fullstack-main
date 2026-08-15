from rest_framework import viewsets, permissions
from .models import Ecole, Classe
from .serializers import ClasseSerializer, EcoleSerializer
from .mixins import SchoolScopeMixin
from .permissions import IsInSameSchool, IsDirectionOrReadOnly


class EcoleViewSet(viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /ecoles/
    - Superadmin : voit tous les établissements
    - Directeur/Prof/Élève : voit UNIQUEMENT son établissement assigné
    - Écriture réservée à la direction (ADMIN/DIRECTEUR)
    """
    serializer_class = EcoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Ecole.objects.filter(is_active=True)
        if user.ecole_id:
            return Ecole.objects.filter(pk=user.ecole_id, is_active=True)
        return Ecole.objects.none()


class ClasseViewSet(SchoolScopeMixin, viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /classes/
    - Isolation automatique via mixin + permission objet
    - Écriture réservée à la direction (ADMIN/DIRECTEUR)
    """
    serializer_class = ClasseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsInSameSchool,
        IsDirectionOrReadOnly,
    ]

    def get_queryset(self):
        # select_related évite les requêtes N+1 sur la FK ecole
        return Classe.objects.filter(is_active=True).select_related("ecole")

    def perform_create(self, serializer):
        # Empêche la création d'une classe dans un autre établissement
        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(ecole=self.request.user.ecole)
