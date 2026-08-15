from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserProfileSecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eleve1", email="eleve1@example.cg", password="Tr3s-Solide!42", role="ELEVE")
        self.client.force_authenticate(self.user)

    def test_role_cannot_be_escalated_via_me_endpoint(self):
        response = self.client.patch(reverse("user_profile"), {"role": "ADMIN"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "ELEVE")

    def test_me_endpoint_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
