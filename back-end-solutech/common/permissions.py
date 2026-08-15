"""Permissions DRF partagées (CDC §7.2)."""

from rest_framework import permissions

from .roles import DIRECTION_ROLES, Role, STAFF_ROLES, has_role
from .scoping import resolve_attr


class IsRole(permissions.BasePermission):
    """Permission générique : l'utilisateur doit avoir l'un des `allowed_roles`."""

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        return has_role(request.user, self.allowed_roles)


class IsDirection(IsRole):
    """Direction d'établissement : rapports, exports et alertes."""

    allowed_roles = DIRECTION_ROLES


class RoleScopePermission(permissions.BasePermission):
    """Isolation objet par école / parent / élève.

    Les sous-classes déclarent les chemins d'attributs vers l'école de l'objet,
    ses parents et son élève, ainsi que les rôles autorisés à atteindre la vue :

        class PedagogyScopePermission(RoleScopePermission):
            ecole_path = "classe.ecole"
            parent_path = "eleve.parents"
            eleve_path = "eleve"
    """

    ecole_path = "ecole"
    parent_path: str | None = None
    eleve_path: str | None = None
    # None = tout utilisateur authentifié
    allowed_roles: tuple[str, ...] | None = None
    # Rôles autorisés à écrire ; None = mêmes rôles qu'en lecture
    write_roles: tuple[str, ...] | None = None

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        if self.allowed_roles is not None and not has_role(user, self.allowed_roles):
            return False
        if request.method not in permissions.SAFE_METHODS and self.write_roles is not None:
            return has_role(user, self.write_roles)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True

        role = getattr(user, "role", None)
        if role in STAFF_ROLES:
            ecole = resolve_attr(obj, self.ecole_path)
            return ecole is not None and ecole == getattr(user, "ecole", None)
        if role == Role.PARENT and self.parent_path:
            parents = resolve_attr(obj, self.parent_path)
            return bool(parents and parents.filter(id=user.id).exists())
        if role == Role.ELEVE and self.eleve_path:
            eleve = resolve_attr(obj, self.eleve_path)
            return eleve is not None and eleve.id == getattr(user, "eleve_id", None)
        return False
