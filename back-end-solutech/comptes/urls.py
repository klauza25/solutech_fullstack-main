from django.urls import path
from .views import UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import CustomTokenObtainPairView


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
]
