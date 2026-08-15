from rest_framework import permissions

class PedagogyScopePermission(permissions.BasePermission):
    """Isolation stricte par école/parent (CDC §7.2)"""

    # Saisie des notes et présences : personnel de l'établissement uniquement.
    WRITE_ROLES = ["ADMIN", "DIRECTEUR", "CENSEUR", "PROFESSEUR"]

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or request.method in permissions.SAFE_METHODS:
            return True
        return user.role in self.WRITE_ROLES

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"]:
            # À affiner avec FK prof→classe en Phase 2
            return user.ecole_id is not None and obj.classe.ecole_id == user.ecole_id
        if user.role == "PARENT":
            return obj.eleve.parents.filter(id=user.id).exists()
        if user.role == "ELEVE":
            return obj.eleve.id == getattr(user, "eleve_id", None)
        return False
