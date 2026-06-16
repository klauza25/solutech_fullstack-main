from django.shortcuts import render
#from django.utils import timezone
from datetime import datetime
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import generics, permissions
from rest_framework.throttling import UserRateThrottle
from .models import User
from .serializers import UserProfileSerializer




def compte(request):
    
    

    date = datetime.now()

    return render(request, "index.html", { 'date':date })



class CustomTokenObtainPairView(TokenObtainPairView):
    """Point d'entrée /login/ avec notre sérialiseur personnalisé"""
    serializer_class = CustomTokenObtainPairSerializer
    
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    """Endpoint /me/ sécurisé : un utilisateur ne voit/modifie que SON profil"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]  # Rate limit configuré dans settings.py

    def get_object(self):
        # 🔒 Sécurité critique : on force la récupération de l'objet connecté
        return self.request.user