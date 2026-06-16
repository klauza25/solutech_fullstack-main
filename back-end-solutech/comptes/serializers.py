from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Étend le sérialiseur JWT par défaut pour :
    1. Injecter le rôle et le téléphone dans le payload du token (claims)
    2. Retourner les infos utilisateur dans la réponse API (évite une 2e requête)
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 🔐 Claims personnalisés (visibles côté client si décodé, mais signés par le serveur)
        token['role'] = user.role
        token['phone'] = user.phone or ''
        return token

    def validate(self, attrs):
        # Génère access + refresh tokens via la logique parente
        data = super().validate(attrs)
        
        # Ajoute les données utilisateur dans la réponse HTTP
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'role': self.user.role,
            'email': self.user.email or '',
            'phone': self.user.phone or '',
        })
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour afficher/modifier le profil (étape suivante)"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'date_joined')
        read_only_fields = ('id', 'date_joined')