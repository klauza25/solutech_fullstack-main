from datetime import date
from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from ecoles.models import Classe, Ecole
from eleves.models import Eleve, LienFamille
from eleves.permissions import EleveScopePermission
from eleves.serializers import EleveDetailSerializer, EleveListSerializer

User = get_user_model()


def make_ecole(nom="CEG Moungali", code="BZV-CEG-001"):
    return Ecole.objects.create(
        nom=nom, code_mepsa=code, cycles="COLLEGE", region="Brazzaville"
    )


def make_user(username, role="PROFESSEUR", ecole=None, superuser=False):
    create = User.objects.create_superuser if superuser else User.objects.create_user
    return create(
        username=username,
        email=f"{username}@ecole.cg",
        password="pwd",
        role=role,
        ecole=ecole,
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


class EleveModelTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()

    def test_defaults(self):
        eleve = make_eleve(self.ecole)
        self.assertEqual(eleve.statut, "ACTIF")
        self.assertFalse(eleve.est_redoublant)
        self.assertEqual(eleve.historique_redoublements, [])
        self.assertTrue(eleve.is_active)

    def test_str_uppercases_the_family_name(self):
        eleve = make_eleve(self.ecole)
        self.assertEqual(str(eleve), "KOUMOU Marie (M2026-BZV-000001)")

    def test_matricule_is_unique(self):
        make_eleve(self.ecole)
        with self.assertRaises(IntegrityError):
            make_eleve(self.ecole, prenom="Paul")

    def test_school_is_protected_against_deletion(self):
        from django.db.models import ProtectedError

        make_eleve(self.ecole)
        with self.assertRaises(ProtectedError):
            self.ecole.delete()

    def test_class_is_set_to_null_when_deleted(self):
        classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        eleve = make_eleve(self.ecole, classe_actuelle=classe)

        classe.delete()
        eleve.refresh_from_db()

        self.assertIsNone(eleve.classe_actuelle)


class LienFamilleTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.eleve = make_eleve(self.ecole)
        self.parent = make_user("papa", role="PARENT", ecole=self.ecole)
        self.parent.first_name = "Jean"
        self.parent.last_name = "Koumou"
        self.parent.save(update_fields=["first_name", "last_name"])

    def test_defaults_and_str(self):
        lien = LienFamille.objects.create(
            eleve=self.eleve, parent=self.parent, type_lien="PERE"
        )
        self.assertFalse(lien.est_responsable_financier)
        self.assertTrue(lien.est_contact_principal)
        self.assertEqual(str(lien), "Jean Koumou → Marie (Père)")

    def test_a_parent_can_only_be_linked_once_per_student(self):
        LienFamille.objects.create(eleve=self.eleve, parent=self.parent, type_lien="PERE")
        with self.assertRaises(IntegrityError):
            LienFamille.objects.create(eleve=self.eleve, parent=self.parent, type_lien="TUTEUR")

    def test_link_feeds_the_parents_relation(self):
        LienFamille.objects.create(eleve=self.eleve, parent=self.parent, type_lien="PERE")
        self.assertEqual(list(self.eleve.parents.all()), [self.parent])
        self.assertEqual(list(self.parent.enfants.all()), [self.eleve])


class EleveSerializerTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.eleve = make_eleve(self.ecole, classe_actuelle=self.classe)

    def test_list_serializer_stays_light_and_flattens_related_names(self):
        data = EleveListSerializer(self.eleve).data

        self.assertEqual(data["classe_nom"], "6ème A")
        self.assertEqual(data["ecole_nom"], "CEG Moungali")
        self.assertNotIn("notes_medicales", data)
        self.assertEqual(
            set(data),
            {
                "id",
                "matricule_mepsa",
                "nom",
                "prenom",
                "genre",
                "classe_nom",
                "ecole_nom",
                "statut",
                "est_redoublant",
            },
        )

    def test_detail_serializer_exposes_family_links(self):
        parent = make_user("maman", role="PARENT", ecole=self.ecole)
        LienFamille.objects.create(
            eleve=self.eleve, parent=parent, type_lien="MERE", est_responsable_financier=True
        )

        data = EleveDetailSerializer(self.eleve).data

        self.assertEqual(len(data["liens_familiaux"]), 1)
        self.assertEqual(data["liens_familiaux"][0]["type_lien"], "MERE")
        self.assertTrue(data["liens_familiaux"][0]["est_responsable_financier"])
        self.assertIn("notes_medicales", data)

    def test_repeat_history_is_read_only(self):
        serializer = EleveDetailSerializer()
        self.assertTrue(serializer.fields["historique_redoublements"].read_only)


class EleveScopePermissionTests(TestCase):
    def setUp(self):
        self.permission = EleveScopePermission()
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole("CEG Bacongo", "BZV-CEG-002")
        self.eleve = make_eleve(self.ecole)

    def _request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return request

    def test_authenticated_business_roles_have_access(self):
        for role in ["ADMIN", "DIRECTEUR", "INSPECTEUR", "PROFESSEUR", "PARENT"]:
            with self.subTest(role=role):
                user = make_user(f"u-{role}", role=role, ecole=self.ecole)
                self.assertTrue(self.permission.has_permission(self._request(user), None))

    def test_anonymous_user_has_no_access(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), None))

    def test_eleve_role_has_no_list_access(self):
        user = make_user("eleve1", role="ELEVE", ecole=self.ecole)
        self.assertFalse(self.permission.has_permission(self._request(user), None))

    def test_superuser_sees_any_student(self):
        user = make_user("root", superuser=True)
        self.assertTrue(
            self.permission.has_object_permission(self._request(user), None, self.eleve)
        )

    def test_direction_is_limited_to_its_own_school(self):
        allowed = make_user("dir", role="DIRECTEUR", ecole=self.ecole)
        denied = make_user("dir2", role="DIRECTEUR", ecole=self.autre_ecole)

        self.assertTrue(
            self.permission.has_object_permission(self._request(allowed), None, self.eleve)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(denied), None, self.eleve)
        )

    def test_teacher_is_limited_to_its_own_school(self):
        allowed = make_user("prof", role="PROFESSEUR", ecole=self.ecole)
        denied = make_user("prof2", role="PROFESSEUR", ecole=self.autre_ecole)

        self.assertTrue(
            self.permission.has_object_permission(self._request(allowed), None, self.eleve)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(denied), None, self.eleve)
        )

    def test_parent_only_sees_its_own_children(self):
        parent = make_user("papa", role="PARENT", ecole=self.ecole)
        autre_parent = make_user("tiers", role="PARENT", ecole=self.ecole)
        LienFamille.objects.create(eleve=self.eleve, parent=parent, type_lien="PERE")

        self.assertTrue(
            self.permission.has_object_permission(self._request(parent), None, self.eleve)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(autre_parent), None, self.eleve)
        )

    def test_unknown_role_is_denied(self):
        user = make_user("eleve1", role="ELEVE", ecole=self.ecole)
        self.assertFalse(
            self.permission.has_object_permission(self._request(user), None, self.eleve)
        )


class EleveViewSetScopeTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole("CEG Bacongo", "BZV-CEG-002")
        self.eleve = make_eleve(self.ecole)
        self.eleve_autre_ecole = make_eleve(self.autre_ecole, matricule="M2026-BZV-000002")
        self.inactif = make_eleve(self.ecole, matricule="M2026-BZV-000003", is_active=False)
        self.client = APIClient()
        self.url = reverse("eleve-list")

    def _matricules(self, response):
        return {row["matricule_mepsa"] for row in response.data["results"]}

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_superuser_sees_all_active_students(self):
        self.client.force_authenticate(make_user("root", superuser=True))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._matricules(response),
            {self.eleve.matricule_mepsa, self.eleve_autre_ecole.matricule_mepsa},
        )

    def test_direction_only_sees_its_own_school(self):
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))
        response = self.client.get(self.url)
        self.assertEqual(self._matricules(response), {self.eleve.matricule_mepsa})

    def test_teacher_without_school_sees_nothing(self):
        self.client.force_authenticate(make_user("prof", role="PROFESSEUR"))
        response = self.client.get(self.url)
        self.assertEqual(self._matricules(response), set())

    def test_parent_only_sees_its_children(self):
        parent = make_user("papa", role="PARENT", ecole=self.ecole)
        LienFamille.objects.create(eleve=self.eleve, parent=parent, type_lien="PERE")
        self.client.force_authenticate(parent)

        response = self.client.get(self.url)

        self.assertEqual(self._matricules(response), {self.eleve.matricule_mepsa})

    def test_detail_uses_the_detail_serializer(self):
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))
        response = self.client.get(reverse("eleve-detail", args=[self.eleve.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("liens_familiaux", response.data)

    def test_student_of_another_school_is_not_reachable(self):
        self.client.force_authenticate(make_user("dir", role="DIRECTEUR", ecole=self.ecole))
        response = self.client.get(reverse("eleve-detail", args=[self.eleve_autre_ecole.pk]))
        self.assertEqual(response.status_code, 404)


def build_workbook(rows):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Matricule", "Nom", "Prenom", "Genre", "Date de naissance"])
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return SimpleUploadedFile(
        "eleves.xlsx",
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


class EleveImportExcelTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.user = make_user("dir", role="DIRECTEUR", ecole=self.ecole)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse("eleve-import-excel")

    def test_missing_file_returns_400(self):
        response = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Fichier Excel requis")

    def test_creates_students_from_the_spreadsheet(self):
        upload = build_workbook(
            [
                ["M2026-BZV-000010", "Koumou", "Marie", "F", date(2012, 5, 4)],
                ["M2026-BZV-000011", "Bakala", "Paul", "M", date(2011, 2, 1)],
            ]
        )

        response = self.client.post(self.url, {"file": upload}, format="multipart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"]["created"], 2)
        self.assertEqual(response.data["results"]["updated"], 0)
        self.assertEqual(Eleve.objects.count(), 2)
        self.assertEqual(Eleve.objects.first().ecole, self.ecole)

    def test_existing_matricule_is_updated_not_duplicated(self):
        make_eleve(self.ecole, matricule="M2026-BZV-000010", nom="Ancien")
        upload = build_workbook(
            [["M2026-BZV-000010", "Koumou", "Marie", "F", date(2012, 5, 4)]]
        )

        response = self.client.post(self.url, {"file": upload}, format="multipart")

        self.assertEqual(response.data["results"]["updated"], 1)
        self.assertEqual(Eleve.objects.count(), 1)
        self.assertEqual(Eleve.objects.get().nom, "Koumou")

    def test_empty_matricule_cell_is_imported_as_the_string_none(self):
        # Bug connu : `str(row[0]).strip()` transforme une cellule vide en "None",
        # la ligne n'est donc pas ignorée comme prévu.
        upload = build_workbook(
            [
                [None, "Sans", "Matricule", "F", date(2012, 5, 4)],
                ["M2026-BZV-000012", "Koumou", "Marie", "F", date(2012, 5, 4)],
            ]
        )

        response = self.client.post(self.url, {"file": upload}, format="multipart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"]["created"], 2)
        self.assertTrue(Eleve.objects.filter(matricule_mepsa="None").exists())

    def test_invalid_row_rolls_back_the_whole_import(self):
        upload = build_workbook(
            [
                ["M2026-BZV-000013", "Koumou", "Marie", "F", date(2012, 5, 4)],
                ["M2026-BZV-000014", "Bakala", "Paul", "M", "date-invalide"],
            ]
        )

        response = self.client.post(self.url, {"file": upload}, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Eleve.objects.count(), 0)

    def test_rejects_more_than_five_hundred_rows(self):
        rows = [
            [f"M2026-BZV-{index:06d}", "Koumou", "Marie", "F", date(2012, 5, 4)]
            for index in range(501)
        ]

        response = self.client.post(self.url, {"file": build_workbook(rows)}, format="multipart")

        self.assertEqual(response.status_code, 413)
        self.assertEqual(Eleve.objects.count(), 0)

    def test_non_excel_upload_returns_400(self):
        upload = SimpleUploadedFile("eleves.xlsx", b"pas-un-classeur", content_type="text/plain")
        response = self.client.post(self.url, {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, 400)
