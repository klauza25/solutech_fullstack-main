from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvaluationViewSet, PresenceViewSet

router = DefaultRouter()
router.register(r"evaluations", EvaluationViewSet, basename="evaluation")
router.register(r"presences", PresenceViewSet, basename="presence")

urlpatterns = [
    path("", include(router.urls)),
]
