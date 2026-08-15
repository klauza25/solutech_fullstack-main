from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from rest_framework.exceptions import ValidationError

from ecoles.mixins import SchoolScopeMixin
from ecoles.models import Classe, Ecole
from ecoles.permissions import IsInSameSchool
from ecoles.serializers import ClasseSerializer, EcoleSerializer

User = get_user_model()


def make_ecole(**overrides):
    fields = {
        "nom": "CEG Moungali",
        "code_mepsa": "BZV-CEG-001",
        "cycles": "COLLEGE",
        "region": "Brazzaville",
    }
    fields.update(overrides)
    return Ecole.objects.create(**fields)


class EcoleModelTests(TestCase):
    def test_defaults(self):
        ecole = make_ecole()
        self.assertEqual(ecole.type, "PUBLIC")
        self.assertTrue(ecole.is_active)

    def test_str_shows_type_label_and_region(self):
        ecole = make_ecole(type="CONFESSIONNEL")
        self.assertEqual(
            str(ecole), "CEG Moungali (Établissement confessionnel) — Brazzaville"
        )

    def test_code_mepsa_is_unique(self):
        make_ecole()
        with self.assertRaises(IntegrityError):
            make_ecole(nom="Autre école")


class ClasseModelTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()

    def test_defaults_and_str(self):
        classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.assertEqual(classe.capacite_max, 45)
        self.assertTrue(classe.is_active)
        self.assertEqual(str(classe), "6ème A — CEG Moungali (6ème)")

    def test_name_is_unique_within_a_school(self):
        Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        with self.assertRaises(IntegrityError):
            Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)

    def test_same_name_allowed_in_another_school(self):
        Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        autre = make_ecole(nom="CEG Bacongo", code_mepsa="BZV-CEG-002")

        classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=autre)

        self.assertEqual(Classe.objects.filter(nom="6ème A").count(), 2)
        self.assertEqual(classe.ecole, autre)

    def test_classes_are_deleted_with_their_school(self):
        Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.ecole.delete()
        self.assertEqual(Classe.objects.count(), 0)


class EcoleSerializerTests(TestCase):
    def _validate_code(self, value):
        serializer = EcoleSerializer()
        return serializer.validate_code_mepsa(value)

    def test_code_is_trimmed_and_uppercased(self):
        self.assertEqual(self._validate_code("  bzv-ceg-042 "), "BZV-CEG-042")

    def test_accepts_boundary_lengths(self):
        self.assertEqual(self._validate_code("PN-LE-01"), "PN-LE-01")
        self.assertEqual(self._validate_code("BZVX-TECHN-0123"), "BZVX-TECHN-0123")

    def test_rejects_malformed_codes(self):
        for value in ["BZV-CEG", "BZVXX-CEG-042", "BZV-CEG-1", "BZV_CEG_042", "BZV-CEG-04A", ""]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self._validate_code(value)

    def test_full_validation_normalizes_the_code(self):
        serializer = EcoleSerializer(
            data={
                "nom": "CEG Moungali",
                "code_mepsa": "bzv-ceg-042",
                "cycles": "COLLEGE",
                "region": "Brazzaville",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["code_mepsa"], "BZV-CEG-042")

    def test_timestamps_are_read_only(self):
        serializer = EcoleSerializer()
        self.assertTrue(serializer.fields["created_at"].read_only)
        self.assertTrue(serializer.fields["updated_at"].read_only)


class ClasseSerializerTests(TestCase):
    def test_exposes_school_name_and_level_label(self):
        ecole = make_ecole()
        classe = Classe.objects.create(nom="Terminale S", niveau="TLE", ecole=ecole)

        data = ClasseSerializer(classe).data

        self.assertEqual(data["ecole_nom"], "CEG Moungali")
        self.assertEqual(data["niveau_display"], "Terminale")
        self.assertEqual(data["capacite_max"], 45)

    def test_rejects_unknown_level(self):
        ecole = make_ecole()
        serializer = ClasseSerializer(
            data={"nom": "6ème A", "niveau": "CM7", "ecole": ecole.pk}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("niveau", serializer.errors)


class IsInSameSchoolTests(TestCase):
    def setUp(self):
        self.permission = IsInSameSchool()
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole(nom="CEG Bacongo", code_mepsa="BZV-CEG-002")
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)

    def _user(self, username, ecole=None, superuser=False):
        create = User.objects.create_superuser if superuser else User.objects.create_user
        return create(username=username, email=f"{username}@ecole.cg", password="pwd", ecole=ecole)

    def _request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return request

    def test_superuser_can_access_any_object(self):
        request = self._request(self._user("root", superuser=True))
        self.assertTrue(self.permission.has_object_permission(request, None, self.classe))

    def test_user_of_the_same_school_is_allowed(self):
        request = self._request(self._user("dir", ecole=self.ecole))
        self.assertTrue(self.permission.has_object_permission(request, None, self.classe))

    def test_user_of_another_school_is_denied(self):
        request = self._request(self._user("dir2", ecole=self.autre_ecole))
        self.assertFalse(self.permission.has_object_permission(request, None, self.classe))

    def test_user_without_school_is_denied(self):
        request = self._request(self._user("orphelin"))
        self.assertFalse(self.permission.has_object_permission(request, None, self.classe))

    def test_object_without_school_attribute_is_denied(self):
        request = self._request(self._user("dir3", ecole=self.ecole))
        self.assertFalse(self.permission.has_object_permission(request, None, object()))


class SchoolScopeMixinTests(TestCase):
    def setUp(self):
        self.ecole = make_ecole()
        self.autre_ecole = make_ecole(nom="CEG Bacongo", code_mepsa="BZV-CEG-002")
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)
        self.autre_classe = Classe.objects.create(
            nom="5ème B", niveau="5EME", ecole=self.autre_ecole
        )

    def _view(self, user, queryset):
        class BaseView:
            def get_queryset(inner):
                return queryset

        class ScopedView(SchoolScopeMixin, BaseView):
            pass

        view = ScopedView()
        request = RequestFactory().get("/")
        request.user = user
        view.request = request
        return view

    def _user(self, username, ecole=None, superuser=False):
        create = User.objects.create_superuser if superuser else User.objects.create_user
        return create(username=username, email=f"{username}@ecole.cg", password="pwd", ecole=ecole)

    def test_superuser_sees_every_row(self):
        view = self._view(self._user("root", superuser=True), Classe.objects.all())
        self.assertEqual(view.get_queryset().count(), 2)

    def test_other_users_only_see_their_school(self):
        view = self._view(self._user("dir", ecole=self.ecole), Classe.objects.all())
        self.assertEqual(list(view.get_queryset()), [self.classe])

    def test_user_without_school_sees_nothing(self):
        view = self._view(self._user("orphelin"), Classe.objects.all())
        self.assertEqual(list(view.get_queryset()), [])

    def test_model_without_school_field_returns_empty_queryset(self):
        view = self._view(self._user("dir2", ecole=self.ecole), Ecole.objects.all())
        self.assertEqual(list(view.get_queryset()), [])
