from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from comptes.models import User
from ecoles.models import Ecole
from .models import Eleve


def make_ecole(code):
    return Ecole.objects.create(nom=f"CEG {code}", code_mepsa=code, cycles="COLLEGE", region="Brazzaville")


class EleveAccessControlTests(APITestCase):
    def setUp(self):
        self.ecole_a = make_ecole("BZV-CEG-001")
        self.ecole_b = make_ecole("BZV-CEG-002")
        self.directeur_a = User.objects.create_user(
            username="dir_a", email="dir_a@example.cg", password="Tr3s-Solide!42", role="DIRECTEUR", ecole=self.ecole_a
        )
        self.prof_a = User.objects.create_user(
            username="prof_a", email="prof_a@example.cg", password="Tr3s-Solide!42", role="PROFESSEUR", ecole=self.ecole_a
        )
        self.eleve_b = Eleve.objects.create(
            matricule_mepsa="M2026-B-001", nom="NGOMA", prenom="Sarah", genre="F",
            date_naissance=date(2012, 3, 4), ecole=self.ecole_b,
        )

    def test_professeur_cannot_create_eleve(self):
        self.client.force_authenticate(self.prof_a)
        response = self.client.post("/api/eleves/eleves/", {
            "matricule_mepsa": "M2026-A-999", "nom": "TEST", "prenom": "Test",
            "genre": "M", "date_naissance": "2012-01-01",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_created_eleve_is_attached_to_own_school(self):
        self.client.force_authenticate(self.directeur_a)
        response = self.client.post("/api/eleves/eleves/", {
            "matricule_mepsa": "M2026-A-001", "nom": "MAKAYA", "prenom": "Paul",
            "genre": "M", "date_naissance": "2012-01-01", "ecole": self.ecole_b.pk,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Eleve.objects.get(matricule_mepsa="M2026-A-001").ecole, self.ecole_a)

    def test_eleve_of_other_school_is_not_visible(self):
        self.client.force_authenticate(self.directeur_a)
        response = self.client.get(f"/api/eleves/eleves/{self.eleve_b.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_medical_fields_hidden_from_professeur(self):
        eleve_a = Eleve.objects.create(
            matricule_mepsa="M2026-A-500", nom="LOUBAKI", prenom="Anne", genre="F",
            date_naissance=date(2011, 5, 5), ecole=self.ecole_a, notes_medicales="Asthme",
        )
        self.client.force_authenticate(self.prof_a)
        response = self.client.get(f"/api/eleves/eleves/{eleve_a.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("notes_medicales", response.data)

        self.client.force_authenticate(self.directeur_a)
        response = self.client.get(f"/api/eleves/eleves/{eleve_a.pk}/")
        self.assertEqual(response.data["notes_medicales"], "Asthme")
