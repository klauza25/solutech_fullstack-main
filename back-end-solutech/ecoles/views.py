from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Classe
from .serializers import ClasseSerializer, EcoleSerializer
from .mixins import SchoolScopeMixin
from .permissions import IsInSameSchool


class EcoleViewSet(SchoolScopeMixin, viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /ecoles/
    - Superadmin : voit tous les établissements
    - Directeur/Prof/Élève : voit UNIQUEMENT son établissement assigné
    """
    serializer_class = EcoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Ecole.objects.filter(is_active=True)
        if user.ecole:
            return Ecole.objects.filter(pk=user.ecole.pk, is_active=True)
        return Ecole.objects.none()

class ClasseViewSet(SchoolScopeMixin, viewsets.ModelViewSet):
    """
    GET/POST/PUT/DELETE /classes/
    - Isolation automatique via mixin + permission objet
    """
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated, IsInSameSchool]

    def get_queryset(self):
        # select_related évite les requêtes N+1 sur la FK ecole
        return Classe.objects.filter(is_active=True).select_related("ecole")

class ClasseViewSet(SchoolScopeMixin, viewsets.ModelViewSet):
    """API /classes/ : filtrée automatiquement par école de l'utilisateur"""
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated, IsInSameSchool]
    # Le mixin SchoolScopeMixin gère déjà get_queryset()