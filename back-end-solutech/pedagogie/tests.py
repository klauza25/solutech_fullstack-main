from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ecoles.models import Classe, Ecole
from eleves.models import Eleve, LienFamille
from pedagogie.models import Evaluation, Matiere, Presence
from pedagogie.permissions import PedagogyScopePermission
from pedagogie.serializers import (
    EvaluationCreateSerializer,
    EvaluationReadSerializer,
    PresenceSerializer,
)

User = get_user_model()


def make_ecole(nom="CEG Moungali", code="BZV-CEG-001"):
    return Ecole.objects.create(
        nom=nom, code_mepsa=code, cycles="COLLEGE", region="Brazzaville"
    )


def make_user(username, role="PROFESSEUR", ecole=None, superuser=False):
    create = User.objects.create_superuser if superuser else User.objects.create_user
    return create(
        username=username, email=f"{username}@ecole.cg", password="pwd", role=role, ecole=ecole
    )


def make_eleve(ecole, matricule="M2026-BZV-000001", **overrides):
    fields = {
        "matricule_mepsa": matricule,
        "nom": "Koumou",
        "prenom": "Marie",
        "genre": "F",
        "date_naissance": date(2012, 5, 4),
        "ecole": ecole,
    }
    fields.update(overrides)
    return Eleve.objects.create(**fields)


class MatiereModelTests(TestCase):
    def test_defaults_and_str(self):
        matiere = Matiere.objects.create(nom="Mathématiques", code="MATH6")
        self.assertEqual(matiere.coefficient_defaut, Decimal("1.0"))
        self.assertTrue(matiere.est_obligatoire)
        self.assertEqual(str(matiere), "Mathématiques (MATH6)")

    def test_code_is_unique(self):
        Matiere.objects.create(nom="Mathématiques", code="MATH6")
        with self.assertRaises(IntegrityError):
            Matiere.objects.create(nom="Maths 6e", code="MATH6")


class EvaluationModelTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.eleve = make_eleve(self.ecole, classe_actuelle=self.classe)
        self.matiere = Matiere.objects.create(nom="Mathématiques", code="MATH6")

    def _evaluation(self, **overrides):
        fields = {
            "eleve": self.eleve,
            "matiere": self.matiere,
            "classe": self.classe,
            "trimestre": 1,
            "type_eval": "DEV",
            "coefficient": Decimal("2.0"),
            "note_sur_20": Decimal("14.50"),
            "date_eval": date(2026, 1, 15),
        }
        fields.update(overrides)
        return Evaluation.objects.create(**fields)

    def test_defaults_and_str(self):
        evaluation = self._evaluation()
        self.assertFalse(evaluation.est_validee)
        self.assertEqual(str(evaluation), "Marie - Mathématiques : 14.50/20")

    def test_one_evaluation_per_student_subject_term_and_type(self):
        self._evaluation()
        with self.assertRaises(IntegrityError):
            self._evaluation(note_sur_20=Decimal("12.00"))

    def test_another_type_in_the_same_term_is_allowed(self):
        self._evaluation()
        other = self._evaluation(type_eval="INT")
        self.assertEqual(Evaluation.objects.count(), 2)
        self.assertEqual(other.type_eval, "INT")


class PresenceModelTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.eleve = make_eleve(self.ecole)

    def _presence(self, **overrides):
        fields = {
            "eleve": self.eleve,
            "classe": self.classe,
            "date": date(2026, 1, 15),
            "trimestre": 1,
            "statut": "ABS",
        }
        fields.update(overrides)
        return Presence.objects.create(**fields)

    def test_str_uses_the_status_label(self):
        self.assertEqual(str(self._presence()), "Marie | 2026-01-15 → Absent non justifié")

    def test_only_one_record_per_student_and_day(self):
        self._presence()
        with self.assertRaises(IntegrityError):
            self._presence(statut="PRE")

    def test_recorded_by_is_kept_null_when_the_user_is_deleted(self):
        user = make_user("prof", ecole=self.ecole)
        presence = self._presence(recorded_by=user)

        user.delete()
        presence.refresh_from_db()

        self.assertIsNone(presence.recorded_by)


class EvaluationSerializerTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.eleve = make_eleve(self.ecole)
        self.matiere = Matiere.objects.create(nom="Mathématiques", code="MATH6")

    def _payload(self, **overrides):
        payload = {
            "eleve": self.eleve.pk,
            "matiere": self.matiere.pk,
            "classe": self.classe.pk,
            "trimestre": 1,
            "type_eval": "DEV",
            "coefficient": "2.0",
            "note_sur_20": "14.50",
            "date_eval": "2026-01-15",
        }
        payload.update(overrides)
        return payload

    def test_accepts_boundary_grades(self):
        for note in ["0.00", "20.00"]:
            with self.subTest(note=note):
                serializer = EvaluationCreateSerializer(data=self._payload(note_sur_20=note))
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_grades_outside_zero_twenty(self):
        for note in ["-1.00", "20.01"]:
            with self.subTest(note=note):
                serializer = EvaluationCreateSerializer(data=self._payload(note_sur_20=note))
                self.assertFalse(serializer.is_valid())
                self.assertIn("note_sur_20", serializer.errors)

    def test_validation_flag_cannot_be_set_at_creation(self):
        self.assertNotIn("est_validee", EvaluationCreateSerializer().fields)

    def test_weighted_average_uses_every_evaluation_of_the_term(self):
        first = Evaluation.objects.create(
            eleve=self.eleve,
            matiere=self.matiere,
            classe=self.classe,
            trimestre=1,
            type_eval="DEV",
            coefficient=Decimal("2.0"),
            note_sur_20=Decimal("16.00"),
            date_eval=date(2026, 1, 15),
        )
        Evaluation.objects.create(
            eleve=self.eleve,
            matiere=self.matiere,
            classe=self.classe,
            trimestre=1,
            type_eval="INT",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("10.00"),
            date_eval=date(2026, 1, 20),
        )

        data = EvaluationReadSerializer(first).data

        self.assertEqual(data["moyenne_trimestrielle"], Decimal("14.00"))
        self.assertEqual(data["matiere_nom"], "Mathématiques")
        self.assertIn("KOUMOU Marie", data["eleve_info"])

    def test_average_ignores_the_other_terms(self):
        evaluation = Evaluation.objects.create(
            eleve=self.eleve,
            matiere=self.matiere,
            classe=self.classe,
            trimestre=1,
            type_eval="DEV",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("12.00"),
            date_eval=date(2026, 1, 15),
        )
        Evaluation.objects.create(
            eleve=self.eleve,
            matiere=self.matiere,
            classe=self.classe,
            trimestre=2,
            type_eval="DEV",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("4.00"),
            date_eval=date(2026, 4, 15),
        )

        data = EvaluationReadSerializer(evaluation).data

        self.assertEqual(data["moyenne_trimestrielle"], Decimal("12.00"))


class PresenceSerializerTests(TestCase):
    def test_exposes_related_labels_and_protects_audit_fields(self):
        ecole = make_ecole()
        classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=ecole)
        presence = Presence.objects.create(
            eleve=make_eleve(ecole),
            classe=classe,
            date=date(2026, 1, 15),
            trimestre=1,
            statut="ABS",
        )

        data = PresenceSerializer(presence).data

        self.assertEqual(data["classe_nom"], "6ème A")
        self.assertIn("KOUMOU Marie", data["eleve_info"])
        self.assertTrue(PresenceSerializer().fields["recorded_by"].read_only)
        self.assertTrue(PresenceSerializer().fields["created_at"].read_only)

    def test_rejects_unknown_status(self):
        ecole = make_ecole()
        classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=ecole)
        serializer = PresenceSerializer(
            data={
                "eleve": make_eleve(ecole).pk,
                "classe": classe.pk,
                "date": "2026-01-15",
                "trimestre": 1,
                "statut": "XXX",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("statut", serializer.errors)


class PedagogyScopePermissionTests(TestCase):
    def setUp(self):
        self.permission = PedagogyScopePermission()
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole("CEG Bacongo", "BZV-CEG-002")
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.eleve = make_eleve(self.ecole)
        self.presence = Presence.objects.create(
            eleve=self.eleve,
            classe=self.classe,
            date=date(2026, 1, 15),
            trimestre=1,
            statut="ABS",
        )

    def _request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return request

    def test_any_authenticated_user_passes_the_view_level_check(self):
        user = make_user("eleve1", role="ELEVE", ecole=self.ecole)
        self.assertTrue(self.permission.has_permission(self._request(user), None))

    def test_anonymous_user_is_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), None))

    def test_superuser_needs_the_same_school(self):
        # Le superadmin passe par la même branche que la direction : sans école
        # rattachée il n'accède pas aux objets.
        root = make_user("root", superuser=True)
        self.assertFalse(
            self.permission.has_object_permission(self._request(root), None, self.presence)
        )

    def test_direction_and_teachers_are_scoped_to_their_school(self):
        for role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR"]:
            with self.subTest(role=role):
                allowed = make_user(f"ok-{role}", role=role, ecole=self.ecole)
                denied = make_user(f"ko-{role}", role=role, ecole=self.autre_ecole)
                self.assertTrue(
                    self.permission.has_object_permission(
                        self._request(allowed), None, self.presence
                    )
                )
                self.assertFalse(
                    self.permission.has_object_permission(
                        self._request(denied), None, self.presence
                    )
                )

    def test_parent_only_accesses_records_of_its_children(self):
        parent = make_user("papa", role="PARENT", ecole=self.ecole)
        autre = make_user("tiers", role="PARENT", ecole=self.ecole)
        LienFamille.objects.create(eleve=self.eleve, parent=parent, type_lien="PERE")

        self.assertTrue(
            self.permission.has_object_permission(self._request(parent), None, self.presence)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(autre), None, self.presence)
        )

    def test_student_role_is_denied_without_a_student_link(self):
        eleve_user = make_user("eleve1", role="ELEVE", ecole=self.ecole)
        self.assertFalse(
            self.permission.has_object_permission(self._request(eleve_user), None, self.presence)
        )


class EvaluationViewSetTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole("CEG Bacongo", "BZV-CEG-002")
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.autre_classe = Classe.objects.create(
            nom="6ème B", niveau="6EME", ecole=self.autre_ecole
        )
        self.matiere = Matiere.objects.create(nom="Mathématiques", code="MATH6")
        self.eleve = make_eleve(self.ecole)
        self.autre_eleve = make_eleve(self.autre_ecole, matricule="M2026-BZV-000002")
        self.evaluation = Evaluation.objects.create(
            eleve=self.eleve,
            matiere=self.matiere,
            classe=self.classe,
            trimestre=1,
            type_eval="DEV",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("12.00"),
            date_eval=date(2026, 1, 15),
        )
        Evaluation.objects.create(
            eleve=self.autre_eleve,
            matiere=self.matiere,
            classe=self.autre_classe,
            trimestre=1,
            type_eval="DEV",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("8.00"),
            date_eval=date(2026, 1, 15),
        )
        self.client = APIClient()
        self.url = reverse("evaluation-list")

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_superuser_sees_every_evaluation(self):
        self.client.force_authenticate(make_user("root", superuser=True))
        self.assertEqual(self.client.get(self.url).data["count"], 2)

    def test_direction_only_sees_its_school(self):
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))
        response = self.client.get(self.url)

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.evaluation.id)

    def test_parent_sees_the_evaluations_of_its_children(self):
        parent = make_user("papa", role="PARENT", ecole=self.ecole)
        LienFamille.objects.create(eleve=self.eleve, parent=parent, type_lien="PERE")
        self.client.force_authenticate(parent)

        self.assertEqual(self.client.get(self.url).data["count"], 1)

    def test_read_uses_the_read_serializer(self):
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))
        response = self.client.get(self.url)
        self.assertIn("moyenne_trimestrielle", response.data["results"][0])

    def test_creation_persists_the_evaluation(self):
        self.client.force_authenticate(make_user("prof", ecole=self.ecole))
        response = self.client.post(
            self.url,
            {
                "eleve": self.eleve.pk,
                "matiere": self.matiere.pk,
                "classe": self.classe.pk,
                "trimestre": 2,
                "type_eval": "INT",
                "coefficient": "1.0",
                "note_sur_20": "15.00",
                "date_eval": "2026-04-15",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created = Evaluation.objects.get(trimestre=2)
        self.assertEqual(created.date_eval, date(2026, 4, 15))
        self.assertFalse(created.est_validee)

    def test_creation_requires_the_evaluation_date(self):
        self.client.force_authenticate(make_user("prof", ecole=self.ecole))
        response = self.client.post(
            self.url,
            {
                "eleve": self.eleve.pk,
                "matiere": self.matiere.pk,
                "classe": self.classe.pk,
                "trimestre": 2,
                "type_eval": "INT",
                "coefficient": "1.0",
                "note_sur_20": "15.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("date_eval", response.data)

    def test_creation_rejects_an_out_of_range_grade(self):
        self.client.force_authenticate(make_user("prof", ecole=self.ecole))
        response = self.client.post(
            self.url,
            {
                "eleve": self.eleve.pk,
                "matiere": self.matiere.pk,
                "classe": self.classe.pk,
                "trimestre": 3,
                "type_eval": "INT",
                "coefficient": "1.0",
                "note_sur_20": "21.00",
                "date_eval": "2026-05-15",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("note_sur_20", response.data)


class PresenceViewSetTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole("CEG Bacongo", "BZV-CEG-002")
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.autre_classe = Classe.objects.create(
            nom="6ème B", niveau="6EME", ecole=self.autre_ecole
        )
        self.eleve = make_eleve(self.ecole)
        self.autre_eleve = make_eleve(self.autre_ecole, matricule="M2026-BZV-000002")
        self.client = APIClient()
        self.url = reverse("presence-list")

    def _presence(self, eleve, classe, day, statut="ABS"):
        return Presence.objects.create(
            eleve=eleve, classe=classe, date=day, trimestre=1, statut=statut
        )

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_queryset_is_scoped_to_the_school(self):
        self._presence(self.eleve, self.classe, date(2026, 1, 15))
        self._presence(self.autre_eleve, self.autre_classe, date(2026, 1, 15))
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))

        response = self.client.get(self.url)

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["classe_nom"], "6ème A")

    def test_creation_stamps_the_recording_user(self):
        prof = make_user("prof", ecole=self.ecole)
        self.client.force_authenticate(prof)

        response = self.client.post(
            self.url,
            {
                "eleve": self.eleve.pk,
                "classe": self.classe.pk,
                "date": "2026-01-16",
                "trimestre": 1,
                "statut": "ABS",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Presence.objects.get().recorded_by, prof)

    def test_dropout_alerts_are_restricted_to_the_direction(self):
        self.client.force_authenticate(make_user("prof", ecole=self.ecole))
        response = self.client.get(reverse("presence-dropout-alerts"))
        self.assertEqual(response.status_code, 403)

    def test_dropout_alerts_flag_three_absences_within_thirty_days(self):
        today = timezone.now().date()
        for offset in range(3):
            self._presence(self.eleve, self.classe, today - timedelta(days=offset))
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))

        response = self.client.get(reverse("presence-dropout-alerts"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["alerts"][0]["eleve__id"], self.eleve.id)
        self.assertEqual(response.data["alerts"][0]["alerte_type"], "Absences répétées")

    def test_dropout_alerts_ignore_two_absences_and_old_ones(self):
        today = timezone.now().date()
        self._presence(self.eleve, self.classe, today)
        self._presence(self.eleve, self.classe, today - timedelta(days=1))
        self._presence(self.eleve, self.classe, today - timedelta(days=45))
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))

        response = self.client.get(reverse("presence-dropout-alerts"))

        self.assertEqual(response.data["count"], 0)

    def test_dropout_alerts_flag_a_term_average_below_eight(self):
        Evaluation.objects.create(
            eleve=self.eleve,
            matiere=Matiere.objects.create(nom="Mathématiques", code="MATH6"),
            classe=self.classe,
            trimestre=1,
            type_eval="DEV",
            coefficient=Decimal("1.0"),
            note_sur_20=Decimal("7.00"),
            date_eval=date(2026, 1, 15),
        )
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))

        response = self.client.get(reverse("presence-dropout-alerts"))

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["alerts"][0]["alerte_type"], "Moyenne < 8/20")

    def test_csv_export_is_restricted_to_the_direction(self):
        self.client.force_authenticate(make_user("prof", ecole=self.ecole))
        response = self.client.get(reverse("presence-export-csv"))
        self.assertEqual(response.status_code, 403)

    def test_csv_export_streams_the_scoped_rows(self):
        self._presence(self.eleve, self.classe, date(2026, 1, 15))
        self._presence(self.autre_eleve, self.autre_classe, date(2026, 1, 15))
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))

        response = self.client.get(reverse("presence-export-csv"))
        content = b"".join(response.streaming_content).decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(content.startswith("\ufeffMatricule,Nom,Prenom,Classe,Date,Statut"))
        self.assertIn(self.eleve.matricule_mepsa, content)
        self.assertNotIn(self.autre_eleve.matricule_mepsa, content)
