from rest_framework import permissions

class ExamenScopePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        # Directeur/Censeur/Inspecteur : accès établissement
        if user.role in ["ADMIN", "DIRECTEUR", "CENSEUR", "INSPECTEUR"]:
            # (À affiner si FK ecole sur SessionExamen est ajoutée plus tard)
            return True
        # Enseignant : saisie uniquement si session PREP/SAISIE
        if user.role == "PROFESSEUR":
            from .models import SessionExamen
            if isinstance(obj, SessionExamen):
                return obj.statut in ["PREP", "SAISIE"]
            return True
        return False
