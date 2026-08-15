from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from comptes.models import User
from comptes.permissions import (
    IsAdminOrDirecteur,
    IsEleveOrParent,
    IsProfesseur,
    IsRole,
)
from comptes.serializers import CustomTokenObtainPairSerializer, UserProfileSerializer
from ecoles.models import Ecole


class UserManagerTests(TestCase):
    def test_create_user_hashes_password_and_normalizes_email(self):
        user = User.objects.create_user(
            username="prof1", email="Prof1@Ecole.CG", password="secret-pwd"
        )

        self.assertEqual(user.email, "Prof1@ecole.cg")
        self.assertNotEqual(user.password, "secret-pwd")
        self.assertTrue(user.check_password("secret-pwd"))
        self.assertEqual(user.role, User.RoleChoices.ELEVE)
        self.assertFalse(user.is_staff)

    def test_create_user_requires_a_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="x@ecole.cg", password="pwd")

    def test_create_user_without_email_violates_the_column_constraint(self):
        # Bug connu : le manager convertit l'email absent en None alors que la
        # colonne AbstractUser.email est NOT NULL (défaut attendu : chaîne vide).
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="sans-email", password="pwd")

    def test_create_superuser_sets_admin_role_and_flags(self):
        admin = User.objects.create_superuser(
            username="root", email="root@ecole.cg", password="pwd"
        )

        self.assertEqual(admin.role, "ADMIN")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_keeps_explicit_role(self):
        admin = User.objects.create_superuser(
            username="inspecteur", email="i@ecole.cg", password="pwd", role="INSPECTEUR"
        )
        self.assertEqual(admin.role, "INSPECTEUR")


class UserModelTests(TestCase):
    def test_str_uses_full_name_when_available(self):
        user = User.objects.create_user(
            username="mkoumou",
            email="m@ecole.cg",
            password="pwd",
            first_name="Marie",
            last_name="Koumou",
            role="DIRECTEUR",
        )
        self.assertEqual(str(user), "Marie Koumou (Directeur / Proviseur / Censeur)")

    def test_str_falls_back_to_username(self):
        user = User.objects.create_user(
            username="mkoumou", email="m@ecole.cg", password="pwd", role="PROFESSEUR"
        )
        self.assertEqual(str(user), "mkoumou (Professeur / Instituteur)")

    def test_phone_is_unique(self):
        User.objects.create_user(
            username="a", email="a@ecole.cg", password="pwd", phone="+242060000001"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="b", email="b@ecole.cg", password="pwd", phone="+242060000001"
            )

    def test_ecole_is_cleared_when_the_school_is_deleted(self):
        ecole = Ecole.objects.create(
            nom="CEG Moungali", code_mepsa="BZV-CEG-001", cycles="COLLEGE", region="Brazzaville"
        )
        user = User.objects.create_user(
            username="dir", email="dir@ecole.cg", password="pwd", ecole=ecole
        )

        ecole.delete()
        user.refresh_from_db()

        self.assertIsNone(user.ecole)


class RolePermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def _user(self, role):
        return User.objects.create_user(
            username=f"u-{role}", email=f"{role}@ecole.cg", password="pwd", role=role
        )

    def test_base_class_allows_nothing(self):
        self.assertFalse(IsRole().has_permission(self._request(self._user("ADMIN")), None))

    def test_admin_or_directeur_permission(self):
        permission = IsAdminOrDirecteur()
        self.assertTrue(permission.has_permission(self._request(self._user("ADMIN")), None))
        self.assertTrue(permission.has_permission(self._request(self._user("DIRECTEUR")), None))
        self.assertFalse(permission.has_permission(self._request(self._user("PROFESSEUR")), None))

    def test_professeur_permission(self):
        permission = IsProfesseur()
        self.assertTrue(permission.has_permission(self._request(self._user("PROFESSEUR")), None))
        self.assertFalse(permission.has_permission(self._request(self._user("ELEVE")), None))

    def test_eleve_or_parent_permission(self):
        permission = IsEleveOrParent()
        self.assertTrue(permission.has_permission(self._request(self._user("ELEVE")), None))
        self.assertTrue(permission.has_permission(self._request(self._user("PARENT")), None))
        self.assertFalse(permission.has_permission(self._request(self._user("INSPECTEUR")), None))

    def test_anonymous_user_is_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(
            IsAdminOrDirecteur().has_permission(self._request(AnonymousUser()), None)
        )


class CustomTokenSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="directeur",
            email="directeur@ecole.cg",
            password="pwd-solide",
            role="DIRECTEUR",
            phone="+242060000002",
        )

    def test_token_embeds_role_and_phone_claims(self):
        token = CustomTokenObtainPairSerializer.get_token(self.user)
        self.assertEqual(token["role"], "DIRECTEUR")
        self.assertEqual(token["phone"], "+242060000002")

    def test_phone_claim_is_empty_string_when_missing(self):
        self.user.phone = None
        self.user.save(update_fields=["phone"])
        token = CustomTokenObtainPairSerializer.get_token(self.user)
        self.assertEqual(token["phone"], "")

    def test_validate_returns_tokens_and_user_payload(self):
        serializer = CustomTokenObtainPairSerializer(
            data={"username": "directeur", "password": "pwd-solide"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        data = serializer.validated_data
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["username"], "directeur")
        self.assertEqual(data["role"], "DIRECTEUR")
        self.assertEqual(data["email"], "directeur@ecole.cg")
        self.assertEqual(data["phone"], "+242060000002")

    def test_validate_rejects_wrong_password(self):
        serializer = CustomTokenObtainPairSerializer(
            data={"username": "directeur", "password": "mauvais"}
        )
        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)


class UserProfileSerializerTests(TestCase):
    def test_id_and_date_joined_are_read_only(self):
        serializer = UserProfileSerializer()
        self.assertTrue(serializer.fields["id"].read_only)
        self.assertTrue(serializer.fields["date_joined"].read_only)

    def test_password_is_never_exposed(self):
        user = User.objects.create_user(username="prof", email="prof@ecole.cg", password="pwd")
        data = UserProfileSerializer(user).data
        self.assertNotIn("password", data)
        self.assertEqual(set(data), {"id", "username", "email", "role", "phone", "date_joined"})


class LoginEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="prof", email="prof@ecole.cg", password="pwd-solide", role="PROFESSEUR"
        )

    def test_login_returns_tokens_with_role_claim(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "prof", "password": "pwd-solide"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "PROFESSEUR")
        self.assertEqual(AccessToken(response.data["access"])["role"], "PROFESSEUR")

    def test_login_with_bad_credentials_is_unauthorized(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "prof", "password": "mauvais"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)


class UserProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="prof", email="prof@ecole.cg", password="pwd", role="PROFESSEUR"
        )
        self.other = User.objects.create_user(
            username="autre", email="autre@ecole.cg", password="pwd", role="ELEVE"
        )
        self.url = reverse("user_profile")

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_returns_the_authenticated_user_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], "prof")

    def test_update_only_touches_the_authenticated_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, {"email": "nouveau@ecole.cg"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.email, "nouveau@ecole.cg")
        self.assertEqual(self.other.email, "autre@ecole.cg")

    def test_read_only_fields_are_ignored_on_update(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, {"id": self.other.id}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
