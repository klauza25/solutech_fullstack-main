from rest_framework import permissions

from common.roles import DIRECTION_ROLES, has_role
from common.scoping import resolve_attr


class IsDirectionOrReadOnly(permissions.BasePermission):
    """Lecture pour tout utilisateur authentifié, écriture réservée à la direction."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS or user.is_superuser:
            return True
        return has_role(user, DIRECTION_ROLES)


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
        ecole = resolve_attr(obj, "ecole")
        return ecole is not None and ecole == request.user.ecole
