from rest_framework import permissions

from common.roles import ADMIN_ROLES, Role


class ExamenScopePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        # Directeur/Censeur/Inspecteur : accès établissement
        if user.role in ADMIN_ROLES:
            # (À affiner si FK ecole sur SessionExamen est ajoutée plus tard)
            return True
        # Enseignant : saisie uniquement si session PREP/SAISIE
        if user.role == Role.PROFESSEUR:
            from .models import SessionExamen, StatutSession
            if isinstance(obj, SessionExamen):
                return obj.statut in [StatutSession.PREPARATION, StatutSession.SAISIE]
            return True
        return False
