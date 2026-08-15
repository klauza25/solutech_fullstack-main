from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from ecoles.models import Ecole
from eleves.models import Eleve
from examens.models import (
    CandidatExamen,
    Mention,
    NoteExamen,
    ResultatFinal,
    SessionExamen,
    StatutSession,
)
from examens.permissions import ExamenScopePermission
from examens.serializers import (
    NoteExamenWriteSerializer,
    ResultatFinalSerializer,
    SessionExamenSerializer,
)

User = get_user_model()


def make_session(**overrides):
    fields = {
        "annee_scolaire": "2025-2026",
        "type_examen": "BEPC",
        "serie": "S",
        "date_debut": date(2026, 6, 1),
        "date_fin": date(2026, 6, 10),
    }
    fields.update(overrides)
    return SessionExamen.objects.create(**fields)


def make_candidat(session, numero="BZV-2026-0001", eleve=None):
    return CandidatExamen.objects.create(
        session=session,
        eleve=eleve,
        numero_candidat=numero,
        centre_examen="Lycée de la Révolution",
    )


def make_eleve():
    ecole = Ecole.objects.create(
        nom="CEG Moungali", code_mepsa="BZV-CEG-001", cycles="COLLEGE", region="Brazzaville"
    )
    return Eleve.objects.create(
        matricule_mepsa="M2026-BZV-000001",
        nom="Koumou",
        prenom="Marie",
        genre="F",
        date_naissance=date(2012, 5, 4),
        ecole=ecole,
    )


class SessionExamenModelTests(TestCase):
    def test_defaults_and_str(self):
        session = make_session()

        self.assertEqual(session.statut, StatutSession.PREPARATION)
        self.assertFalse(session.est_proclame)
        self.assertEqual(str(session), "BEPC 2025-2026 (Préparation / Inscriptions ouvertes)")

    def test_one_session_per_year_type_and_series(self):
        make_session()
        with self.assertRaises(IntegrityError):
            make_session(date_debut=date(2026, 7, 1))

    def test_another_series_of_the_same_exam_is_allowed(self):
        make_session()
        make_session(serie="L")
        self.assertEqual(SessionExamen.objects.count(), 2)

    def test_ordering_is_newest_year_first(self):
        old = make_session(annee_scolaire="2024-2025")
        recent = make_session()
        self.assertEqual(list(SessionExamen.objects.all()), [recent, old])


class CandidatExamenModelTests(TestCase):
    def setUp(self):
        self.session = make_session()

    def test_str_falls_back_to_free_candidate(self):
        self.assertEqual(str(make_candidat(self.session)), "BZV-2026-0001 — Candidat libre")

    def test_str_uses_the_student_name(self):
        candidat = make_candidat(self.session, eleve=make_eleve())
        self.assertEqual(str(candidat), "BZV-2026-0001 — Koumou")

    def test_candidate_number_is_unique(self):
        make_candidat(self.session)
        with self.assertRaises(IntegrityError):
            make_candidat(self.session)

    def test_session_is_protected_from_deletion(self):
        make_candidat(self.session)
        with self.assertRaises(ProtectedError):
            self.session.delete()

    def test_student_is_protected_from_deletion(self):
        eleve = make_eleve()
        make_candidat(self.session, eleve=eleve)
        with self.assertRaises(ProtectedError):
            eleve.delete()


class NoteExamenModelTests(TestCase):
    def setUp(self):
        self.candidat = make_candidat(make_session())

    def _note(self, matiere="Mathématiques", note="14.50"):
        return NoteExamen.objects.create(
            candidat=self.candidat,
            matiere=matiere,
            coefficient=Decimal("3.0"),
            note=Decimal(note),
        )

    def test_str_shows_the_candidate_and_the_subject(self):
        self.assertEqual(str(self._note()), "BZV-2026-0001 | Mathématiques : 14.50/20")

    def test_one_note_per_candidate_and_subject(self):
        self._note()
        with self.assertRaises(IntegrityError):
            self._note(note="8.00")

    def test_notes_are_deleted_with_their_candidate(self):
        self._note()
        self.candidat.delete()
        self.assertFalse(NoteExamen.objects.exists())

    def test_author_is_kept_null_when_the_user_is_deleted(self):
        user = User.objects.create_user(
            username="prof", email="prof@ecole.cg", password="pwd", role="PROFESSEUR"
        )
        note = self._note()
        note.saisie_par = user
        note.save()

        user.delete()
        note.refresh_from_db()

        self.assertIsNone(note.saisie_par)


class ResultatFinalModelTests(TestCase):
    def setUp(self):
        self.candidat = make_candidat(make_session())

    def test_str_shows_the_mention(self):
        resultat = ResultatFinal.objects.create(
            candidat=self.candidat,
            moyenne_generale=Decimal("13.50"),
            mention=Mention.ASSEZ_BIEN,
            est_admis=True,
        )

        self.assertEqual(str(resultat), "Résultat BZV-2026-0001 : AB")
        self.assertIsNone(resultat.date_proclamation)

    def test_the_candidate_is_the_primary_key(self):
        ResultatFinal.objects.create(
            candidat=self.candidat, moyenne_generale=Decimal("9.00"), mention=Mention.AJOURNE
        )
        with self.assertRaises(IntegrityError):
            ResultatFinal.objects.create(
                candidat=self.candidat, moyenne_generale=Decimal("11.00"), mention=Mention.PASSABLE
            )

    def test_result_is_deleted_with_its_candidate(self):
        ResultatFinal.objects.create(
            candidat=self.candidat, moyenne_generale=Decimal("9.00"), mention=Mention.AJOURNE
        )
        self.candidat.delete()
        self.assertFalse(ResultatFinal.objects.exists())


class NoteExamenSerializerTests(TestCase):
    def setUp(self):
        self.candidat = make_candidat(make_session())

    def _payload(self, **overrides):
        payload = {
            "candidat": self.candidat.pk,
            "matiere": "Mathématiques",
            "coefficient": "3.0",
            "note": "14.50",
        }
        payload.update(overrides)
        return payload

    def test_accepts_boundary_notes(self):
        for note in ["0.00", "20.00"]:
            with self.subTest(note=note):
                serializer = NoteExamenWriteSerializer(data=self._payload(note=note))
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_notes_outside_zero_twenty(self):
        for note in ["-0.50", "20.01"]:
            with self.subTest(note=note):
                serializer = NoteExamenWriteSerializer(data=self._payload(note=note))
                self.assertFalse(serializer.is_valid())
                self.assertIn("note", serializer.errors)

    def test_rejects_a_non_positive_coefficient(self):
        for coefficient in ["0.0", "-1.0"]:
            with self.subTest(coefficient=coefficient):
                serializer = NoteExamenWriteSerializer(
                    data=self._payload(coefficient=coefficient)
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("coefficient", serializer.errors)

    def test_author_cannot_be_supplied_by_the_client(self):
        self.assertNotIn("saisie_par", NoteExamenWriteSerializer().fields)

    def test_valid_payload_is_persisted(self):
        serializer = NoteExamenWriteSerializer(data=self._payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        note = serializer.save()

        self.assertEqual(note.candidat, self.candidat)
        self.assertEqual(note.note, Decimal("14.50"))
        self.assertIsNone(note.saisie_par)


class ResultatFinalSerializerTests(TestCase):
    def test_exposes_the_candidate_number_and_the_computed_fields(self):
        candidat = make_candidat(make_session())
        proclamation = timezone.now()
        resultat = ResultatFinal.objects.create(
            candidat=candidat,
            moyenne_generale=Decimal("16.25"),
            mention=Mention.TRES_BIEN,
            est_admis=True,
            date_proclamation=proclamation,
        )

        data = ResultatFinalSerializer(resultat).data

        self.assertEqual(data["candidat_numero"], "BZV-2026-0001")
        self.assertEqual(data["moyenne_generale"], "16.25")
        self.assertEqual(data["mention"], Mention.TRES_BIEN)
        self.assertTrue(data["est_admis"])

    def test_computed_fields_are_read_only(self):
        fields = ResultatFinalSerializer().fields
        self.assertTrue(fields["moyenne_generale"].read_only)
        self.assertTrue(fields["mention"].read_only)


class SessionExamenSerializerTests(TestCase):
    def test_counts_the_registered_candidates(self):
        session = make_session()
        make_candidat(session)
        make_candidat(session, numero="BZV-2026-0002")

        data = SessionExamenSerializer(session).data

        self.assertEqual(data["total_candidats"], 2)
        self.assertEqual(data["statut"], StatutSession.PREPARATION)

    def test_proclamation_flag_and_timestamp_are_read_only(self):
        fields = SessionExamenSerializer().fields
        self.assertTrue(fields["est_proclame"].read_only)
        self.assertTrue(fields["created_at"].read_only)

    def test_requires_the_exam_dates(self):
        serializer = SessionExamenSerializer(
            data={"annee_scolaire": "2025-2026", "type_examen": "BEPC", "serie": "S"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_debut", serializer.errors)
        self.assertIn("date_fin", serializer.errors)

    def test_rejects_an_unknown_exam_type(self):
        serializer = SessionExamenSerializer(
            data={
                "annee_scolaire": "2025-2026",
                "type_examen": "DOCTORAT",
                "date_debut": "2026-06-01",
                "date_fin": "2026-06-10",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("type_examen", serializer.errors)


class ExamenScopePermissionTests(TestCase):
    def setUp(self):
        self.permission = ExamenScopePermission()
        self.session = make_session()
        self.candidat = make_candidat(self.session)

    def _request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return request

    def _user(self, username, role):
        return User.objects.create_user(
            username=username, email=f"{username}@ecole.cg", password="pwd", role=role
        )

    def test_authenticated_user_passes_the_view_level_check(self):
        user = self._user("eleve1", "ELEVE")
        self.assertTrue(self.permission.has_permission(self._request(user), None))

    def test_anonymous_user_is_rejected(self):
        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), None))

    def test_superuser_has_full_object_access(self):
        root = User.objects.create_superuser(
            username="root", email="root@ecole.cg", password="pwd", role="ADMIN"
        )
        self.assertTrue(
            self.permission.has_object_permission(self._request(root), None, self.session)
        )

    def test_direction_and_inspection_have_object_access(self):
        for role in ["ADMIN", "DIRECTEUR", "CENSEUR", "INSPECTEUR"]:
            with self.subTest(role=role):
                user = self._user(f"u-{role}", role)
                self.assertTrue(
                    self.permission.has_object_permission(
                        self._request(user), None, self.session
                    )
                )

    def test_teacher_can_only_touch_a_session_open_for_entry(self):
        prof = self._user("prof", "PROFESSEUR")

        for statut, expected in [("PREP", True), ("SAISIE", True), ("COURS", False),
                                 ("PROC", False), ("FERME", False)]:
            with self.subTest(statut=statut):
                self.session.statut = statut
                self.assertEqual(
                    self.permission.has_object_permission(
                        self._request(prof), None, self.session
                    ),
                    expected,
                )

    def test_teacher_keeps_access_to_non_session_objects(self):
        prof = self._user("prof", "PROFESSEUR")
        self.assertTrue(
            self.permission.has_object_permission(self._request(prof), None, self.candidat)
        )

    def test_students_and_parents_are_denied(self):
        for role in ["ELEVE", "PARENT"]:
            with self.subTest(role=role):
                user = self._user(f"u-{role}", role)
                self.assertFalse(
                    self.permission.has_object_permission(
                        self._request(user), None, self.session
                    )
                )
