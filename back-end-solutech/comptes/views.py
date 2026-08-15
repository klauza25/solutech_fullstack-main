from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import generics, permissions
from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle
from .serializers import UserProfileSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Point d'entrée /login/ avec notre sérialiseur personnalisé"""
    serializer_class = CustomTokenObtainPairSerializer
    # Limite les tentatives de connexion (anti-force brute), voir DEFAULT_THROTTLE_RATES['login']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
    
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint /me/ sécurisé : un utilisateur ne voit/modifie que SON profil"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]  # Rate limit configuré dans settings.py

    def get_object(self):
        # 🔒 Sécurité critique : on force la récupération de l'objet connecté
        return self.request.user