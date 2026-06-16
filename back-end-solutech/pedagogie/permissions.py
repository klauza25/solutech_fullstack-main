from rest_framework import permissions

class PedagogyScopePermission(permissions.BasePermission):
    """Isolation stricte par école/parent (CDC §7.2)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR"]:
            return obj.classe.ecole == user.ecole
        if user.role == "PROFESSEUR":
            return obj.classe.ecole == user.ecole  # À affiner avec FK prof→classe en Phase 2
        if user.role == "PARENT":
            return obj.eleve.parents.filter(id=user.id).exists()
        if user.role == "ELEVE":
            return obj.eleve.id == getattr(user, "eleve_id", None)
        return False
