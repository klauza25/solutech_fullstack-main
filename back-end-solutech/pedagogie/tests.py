from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from comptes.models import User
from ecoles.models import Classe, Ecole
from eleves.models import Eleve
from .models import Evaluation, Matiere


class EvaluationWriteAccessTests(APITestCase):
    def setUp(self):
        self.ecole = Ecole.objects.create(
            nom="CEG Moungali", code_mepsa="BZV-CEG-010", cycles="COLLEGE", region="Brazzaville"
        )
        self.classe = Classe.objects.create(nom="6e A", niveau="6EME", ecole=self.ecole)
        self.matiere = Matiere.objects.create(nom="Mathématiques", code="MATH6")
        self.eleve = Eleve.objects.create(
            matricule_mepsa="M2026-A-010", nom="OKEMBA", prenom="Jean", genre="M",
            date_naissance=date(2012, 2, 2), ecole=self.ecole, classe_actuelle=self.classe,
        )
        self.parent = User.objects.create_user(
            username="parent1", email="parent1@example.cg", password="Tr3s-Solide!42",
            role="PARENT",
        )
        self.eleve.parents.add(self.parent)
        self.prof = User.objects.create_user(
            username="prof1", email="prof1@example.cg", password="Tr3s-Solide!42",
            role="PROFESSEUR", ecole=self.ecole,
        )

    def payload(self):
        return {
            "eleve": self.eleve.pk, "matiere": self.matiere.pk, "classe": self.classe.pk,
            "trimestre": 1, "type_eval": "INT", "coefficient": "1.0",
            "note_sur_20": "18.00", "date_eval": "2026-01-15",
        }

    def test_parent_can_read_but_not_create_evaluation(self):
        self.client.force_authenticate(self.parent)
        self.assertEqual(self.client.get("/api/pedagogie/evaluations/").status_code, status.HTTP_200_OK)
        response = self.client.post("/api/pedagogie/evaluations/", self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Evaluation.objects.exists())

    def test_professeur_can_create_evaluation_in_own_school(self):
        self.client.force_authenticate(self.prof)
        response = self.client.post("/api/pedagogie/evaluations/", self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_professeur_cannot_create_evaluation_in_other_school(self):
        autre_ecole = Ecole.objects.create(
            nom="CEG Bacongo", code_mepsa="BZV-CEG-011", cycles="COLLEGE", region="Brazzaville"
        )
        self.prof.ecole = autre_ecole
        self.prof.save(update_fields=["ecole"])
        self.client.force_authenticate(self.prof)
        response = self.client.post("/api/pedagogie/evaluations/", self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
