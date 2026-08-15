"""Classes de vues partagées."""

from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView


class ThrottledAPIView(APIView):
    """APIView authentifiée et limitée en débit (rate limit défini dans settings)."""

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
