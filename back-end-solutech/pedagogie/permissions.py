from common.permissions import RoleScopePermission
from common.roles import DIRECTION_ROLES, Role


class PedagogyScopePermission(RoleScopePermission):
    """Isolation stricte par école/parent (CDC §7.2)"""
    ecole_path = "classe.ecole"
    parent_path = "eleve.parents"
    eleve_path = "eleve"
    # Saisie des notes et présences : personnel de l'établissement uniquement
    # (les parents et élèves gardent un accès en lecture).
    write_roles = DIRECTION_ROLES + (Role.PROFESSEUR,)
