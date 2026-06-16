from rest_framework import permissions

class EleveScopePermission(permissions.BasePermission):
    """
    Contrôle d'accès conforme CDC §7.2 (Protection des mineurs)
    - Directeurs/Admins : voient les élèves de LEUR école
    - Parents : voient UNIQUEMENT leurs enfants liés
    - Professeurs : voient les élèves de leur école (filtrage classe à affiner plus tard)
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or
            user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"] or
            user.role == "PARENT"
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser: return True
        
        if user.role in ["ADMIN", "DIRECTEUR", "INSPECTEUR"]:
            return obj.ecole == user.ecole
            
        if user.role == "PARENT":
            # Vérifie si le parent est bien lié à cet élève
            return obj.parents.filter(id=user.id).exists()
            
        if user.role == "PROFESSEUR":
            # Simplifié : accès école. Le filtrage par classe sera activé avec l'app enseignants
            return obj.ecole == user.ecole
            
        return False