from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EcoleViewSet, ClasseViewSet

router = DefaultRouter()
router.register(r"ecoles", EcoleViewSet, basename="ecole")
router.register(r"classes", ClasseViewSet, basename="classe")

urlpatterns = [
    path("", include(router.urls)),
]