from rest_framework import permissions

DIRECTION_ROLES = ["ADMIN", "DIRECTEUR"]


class IsDirectionOrReadOnly(permissions.BasePermission):
    """Lecture pour tout utilisateur authentifié, écriture réservée à la direction."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.role in DIRECTION_ROLES))


class IsInSameSchool(permissions.BasePermission):
    """
    Permission DRF : vérifie si l'utilisateur et l'objet cible 
    appartiennent au même établissement.
    Utilisé pour les vues de détail/mise à jour.
    """
    def has_object_permission(self, request, view, obj):
        # Superadmin central peut tout voir
        if request.user.is_superuser:
            return True
        # Sinon, l'école doit correspondre
        if hasattr(obj, "ecole"):
            return request.user.ecole_id is not None and obj.ecole_id == request.user.ecole_id
        return False