from common.permissions import RoleScopePermission
from common.roles import Role, STAFF_ROLES


class EleveScopePermission(RoleScopePermission):
    """
    Contrôle d'accès conforme CDC §7.2 (Protection des mineurs)
    - Directeurs/Admins : voient les élèves de LEUR école
    - Parents : voient UNIQUEMENT leurs enfants liés
    - Professeurs : voient les élèves de leur école (filtrage classe à affiner plus tard)
    """
    ecole_path = "ecole"
    parent_path = "parents"
    allowed_roles = STAFF_ROLES + (Role.PARENT,)
    # Création/modification/suppression et import Excel : direction seule
    write_roles = (Role.ADMIN, Role.DIRECTEUR)
