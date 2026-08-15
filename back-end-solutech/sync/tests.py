import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .utils import validate_delta_window

User = get_user_model()


class ValidateDeltaWindowTests(TestCase):
    """La fenêtre de delta doit refuser une date invalide au lieu de la remplacer"""

    def test_date_invalide_leve_une_erreur_de_validation(self):
        with self.assertRaises(ValidationError):
            validate_delta_window("pas-une-date")

    def test_absence_de_parametre_utilise_le_fallback(self):
        window = validate_delta_window(None)
        self.assertLess(window, timezone.now())

    def test_date_valide_est_conservee(self):
        recent = (timezone.now() - timezone.timedelta(days=1)).replace(microsecond=0)
        self.assertEqual(validate_delta_window(recent.isoformat()), recent)


class SyncPushErrorTests(TestCase):
    """Un modèle hors whitelist est une erreur client (400), pas une panne serveur"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="agent", email="agent@example.com", password="motdepasse123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _payload(self, model_name):
        return {
            "device_id": "device-test",
            "operations": [
                {
                    "client_operation_id": str(uuid.uuid4()),
                    "operation_type": "CREATE",
                    "model_name": model_name,
                    "payload": {"nom": "Test"},
                }
            ],
        }

    def test_modele_non_autorise_retourne_400(self):
        response = self.client.post(
            reverse("sync_push"), self._payload("comptes.User"), format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("allowed_models", response.data)

    def test_modele_autorise_est_traite(self):
        response = self.client.post(
            reverse("sync_push"), self._payload("ecoles.Ecole"), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["processed"], 1)


class SyncDeltaErrorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="delta", email="delta@example.com", password="motdepasse123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_last_sync_malforme_retourne_400(self):
        response = self.client.get(reverse("sync_delta"), {"last_sync": "hier"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("last_sync", response.data)
