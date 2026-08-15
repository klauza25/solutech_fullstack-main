from rest_framework import permissions

from common.scoping import resolve_attr


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
