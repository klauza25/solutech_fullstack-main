from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EleveViewSet

router = DefaultRouter()
router.register(r"eleves", EleveViewSet, basename="eleve")

urlpatterns = [
    path("", include(router.urls)),
]