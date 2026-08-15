from common.permissions import RoleScopePermission


class PedagogyScopePermission(RoleScopePermission):
    """Isolation stricte par école/parent (CDC §7.2)"""
    ecole_path = "classe.ecole"
    parent_path = "eleve.parents"
    eleve_path = "eleve"
