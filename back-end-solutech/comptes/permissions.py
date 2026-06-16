from rest_framework import permissions

class IsRole(permissions.BasePermission):
    """Permission générique pour vérifier si l'utilisateur a un rôle spécifique"""
    allowed_roles = []

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.allowed_roles

class IsAdminOrDirecteur(IsRole):
    allowed_roles = ['ADMIN', 'DIRECTEUR']

class IsProfesseur(IsRole):
    allowed_roles = ['PROFESSEUR']

class IsEleveOrParent(IsRole):
    allowed_roles = ['ELEVE', 'PARENT']