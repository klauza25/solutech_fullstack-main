"""Filtrage des données par école / parent / élève (CDC §7.2).

Toutes les apps métier partagent la même règle d'isolation : le superadmin voit
tout, le personnel scolaire voit son école, un parent voit ses enfants et un
élève voit ses propres données. Seuls les chemins ORM changent d'un modèle à
l'autre, ils sont donc déclarés par le ViewSet.
"""

from .roles import Role, STAFF_ROLES


def resolve_attr(obj, path: str):
    """Résout un chemin d'attributs pointé ("classe.ecole") sur un objet."""
    value = obj
    for part in path.split("."):
        if value is None:
            return None
        value = getattr(value, part, None)
    return value


def scope_queryset_by_role(
    queryset,
    user,
    *,
    ecole_path: str = "ecole",
    parent_path: str | None = None,
    eleve_path: str | None = None,
):
    """Restreint `queryset` aux objets visibles par `user`.

    - `ecole_path` : chemin ORM vers l'école de l'objet (ex: "classe__ecole")
    - `parent_path` : chemin ORM vers les parents liés (ex: "eleve__parents")
    - `eleve_path` : chemin ORM vers l'élève concerné (ex: "eleve")
    """
    if not (user and user.is_authenticated):
        return queryset.none()

    if user.is_superuser:
        return queryset

    role = getattr(user, "role", None)
    ecole = getattr(user, "ecole", None)

    if role in STAFF_ROLES:
        return queryset.filter(**{ecole_path: ecole}) if ecole else queryset.none()
    if role == Role.PARENT and parent_path:
        return queryset.filter(**{parent_path: user})
    if role == Role.ELEVE and eleve_path:
        return queryset.filter(**{eleve_path: user})
    return queryset.none()


class RoleScopedQuerysetMixin:
    """Mixin ViewSet : applique `scope_queryset_by_role` à `base_queryset`.

    Le ViewSet déclare la requête de base et les chemins ORM :

        class PresenceViewSet(RoleScopedQuerysetMixin, viewsets.ModelViewSet):
            base_queryset = Presence.objects.select_related("classe__ecole")
            scope_ecole_path = "classe__ecole"
    """

    base_queryset = None
    scope_ecole_path = "ecole"
    scope_parent_path: str | None = None
    scope_eleve_path: str | None = None

    def get_base_queryset(self):
        if self.base_queryset is None:
            raise NotImplementedError(
                f"{type(self).__name__} doit définir `base_queryset` "
                "ou surcharger `get_base_queryset()`."
            )
        return self.base_queryset.all()

    def get_queryset(self):
        return scope_queryset_by_role(
            self.get_base_queryset(),
            self.request.user,
            ecole_path=self.scope_ecole_path,
            parent_path=self.scope_parent_path,
            eleve_path=self.scope_eleve_path,
        )


class SchoolScopeMixin:
    """
    Mixin DRF à hériter dans les ViewSets dont `get_queryset()` est déjà défini.
    Filtre automatiquement les requêtes selon l'école de l'utilisateur connecté.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Superadmin voit tout, les autres voient uniquement leur école
        if user.is_superuser:
            return queryset

        # Filtrage ORM strict (exécuté en SQL, pas en Python)
        if hasattr(queryset.model, "ecole"):
            return queryset.filter(ecole=user.ecole)
        return queryset.none()  # Sécurité : modèle sans champ ecole → rien
