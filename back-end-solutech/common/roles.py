"""Rôles utilisateurs partagés par toutes les apps métier."""


class Role:
    ADMIN = "ADMIN"
    DIRECTEUR = "DIRECTEUR"
    CENSEUR = "CENSEUR"
    INSPECTEUR = "INSPECTEUR"
    PROFESSEUR = "PROFESSEUR"
    PARENT = "PARENT"
    ELEVE = "ELEVE"


# Direction d'établissement : accès aux rapports et exports
DIRECTION_ROLES = (Role.ADMIN, Role.DIRECTEUR, Role.CENSEUR)

# Personnel administratif : accès à toutes les données de son école
ADMIN_ROLES = (Role.ADMIN, Role.DIRECTEUR, Role.CENSEUR, Role.INSPECTEUR)

# Personnel scolaire : administration + enseignants
STAFF_ROLES = ADMIN_ROLES + (Role.PROFESSEUR,)


def has_role(user, roles) -> bool:
    """True si l'utilisateur authentifié possède l'un des rôles demandés."""
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) in roles
    )
