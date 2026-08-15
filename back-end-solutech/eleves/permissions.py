from rest_framework import permissions

class EleveScopePermission(permissions.BasePermission):
    """
    Contrôle d'accès conforme CDC §7.2 (Protection des mineurs)
    - Directeurs/Admins : voient les élèves de LEUR école
    - Parents : voient UNIQUEMENT leurs enfants liés
    - Professeurs : voient les élèves de leur école (filtrage classe à affiner plus tard)
    """
    READ_ROLES = ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR", "PARENT"]
    WRITE_ROLES = ["ADMIN", "DIRECTEUR"]

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            return user.role in self.READ_ROLES
        # Création/modification/suppression (y compris import Excel) : direction seule
        return user.role in self.WRITE_ROLES

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser: return True
        
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR"]:
            return user.ecole_id is not None and obj.ecole_id == user.ecole_id
            
        if user.role == "PARENT":
            # Vérifie si le parent est bien lié à cet élève
            return obj.parents.filter(id=user.id).exists()
            
        if user.role == "PROFESSEUR":
            # Simplifié : accès école. Le filtrage par classe sera activé avec l'app enseignants
            return user.ecole_id is not None and obj.ecole_id == user.ecole_id
            
        return False