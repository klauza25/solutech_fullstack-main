from rest_framework import viewsets

class SchoolScopeMixin:
    """
    Mixin DRF à hériter dans TOUS les ViewSets métier (Élèves, Notes, Classes, etc.)
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
        return queryset.none()  # Sécurité : si le modèle n'a pas de champ ecole, on retourne vide