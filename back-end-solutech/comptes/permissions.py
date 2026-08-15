from common.permissions import IsRole
from common.roles import Role

__all__ = ["IsRole", "IsAdminOrDirecteur", "IsProfesseur", "IsEleveOrParent"]


class IsAdminOrDirecteur(IsRole):
    allowed_roles = (Role.ADMIN, Role.DIRECTEUR)

class IsProfesseur(IsRole):
    allowed_roles = (Role.PROFESSEUR,)

class IsEleveOrParent(IsRole):
    allowed_roles = (Role.ELEVE, Role.PARENT)
