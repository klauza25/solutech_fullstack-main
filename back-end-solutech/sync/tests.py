import json
import uuid
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ecoles.models import Classe, Ecole
from sync.models import SyncQueue, SyncStatus
from sync.serializers import SyncBatchInputSerializer
from sync.utils import log_sync_failure, validate_delta_window

User = get_user_model()


def make_operation(**overrides):
    operation = {
        "client_operation_id": str(uuid.uuid4()),
        "operation_type": "CREATE",
        "model_name": "ecoles.Ecole",
        "payload": {"nom": "CEG Moungali"},
    }
    operation.update(overrides)
    return operation


class ValidateDeltaWindowTests(TestCase):
    def test_returns_seven_day_fallback_when_value_missing(self):
        before = timezone.now()
        result = validate_delta_window(None)
        self.assertAlmostEqual(
            (before - result).total_seconds(), timedelta(days=7).total_seconds(), delta=5
        )

    def test_returns_seven_day_fallback_for_empty_string(self):
        before = timezone.now()
        result = validate_delta_window("")
        self.assertAlmostEqual(
            (before - result).total_seconds(), timedelta(days=7).total_seconds(), delta=5
        )

    def test_parses_iso_value_with_zulu_suffix(self):
        expected = timezone.now() - timedelta(days=2)
        result = validate_delta_window(expected.isoformat().replace("+00:00", "Z"))
        self.assertAlmostEqual((expected - result).total_seconds(), 0, delta=1)

    def test_clamps_values_older_than_thirty_days(self):
        result = validate_delta_window((timezone.now() - timedelta(days=400)).isoformat())
        floor = timezone.now() - timedelta(days=30)
        self.assertAlmostEqual((floor - result).total_seconds(), 0, delta=5)

    def test_keeps_future_values_as_is(self):
        future = timezone.now() + timedelta(days=1)
        result = validate_delta_window(future.isoformat())
        self.assertAlmostEqual((future - result).total_seconds(), 0, delta=1)

    def test_falls_back_on_unparseable_value(self):
        before = timezone.now()
        result = validate_delta_window("pas-une-date")
        self.assertAlmostEqual(
            (before - result).total_seconds(), timedelta(days=7).total_seconds(), delta=5
        )


class LogSyncFailureTests(TestCase):
    def test_emits_json_warning_with_context(self):
        with self.assertLogs("apps.sync", level="WARNING") as captured:
            log_sync_failure("device-1", 42, "MODEL_NOT_ALLOWED", "ecoles.Secret")

        payload = json.loads(captured.records[0].getMessage())
        self.assertEqual(payload["event"], "SYNC_FAILURE")
        self.assertEqual(payload["device_id"], "device-1")
        self.assertEqual(payload["user_id"], 42)
        self.assertEqual(payload["error_type"], "MODEL_NOT_ALLOWED")
        self.assertEqual(payload["details"], "ecoles.Secret")
        self.assertIn("timestamp", payload)

    def test_details_default_to_empty_string(self):
        with self.assertLogs("apps.sync", level="WARNING") as captured:
            log_sync_failure("device-2", 1, "UNKNOWN")

        self.assertEqual(json.loads(captured.records[0].getMessage())["details"], "")


class SyncBatchInputSerializerTests(TestCase):
    def test_accepts_valid_batch(self):
        serializer = SyncBatchInputSerializer(
            data={"device_id": "device-1", "operations": [make_operation()]}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_unknown_operation_type(self):
        serializer = SyncBatchInputSerializer(
            data={"device_id": "device-1", "operations": [make_operation(operation_type="PATCH")]}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("operations", serializer.errors)

    def test_rejects_more_than_fifty_operations(self):
        serializer = SyncBatchInputSerializer(
            data={"device_id": "device-1", "operations": [make_operation() for _ in range(51)]}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("operations", serializer.errors)

    def test_rejects_missing_device_id(self):
        serializer = SyncBatchInputSerializer(data={"operations": [make_operation()]})
        self.assertFalse(serializer.is_valid())
        self.assertIn("device_id", serializer.errors)


class SyncQueueModelTests(TestCase):
    def test_str_contains_operation_model_status_and_device(self):
        user = User.objects.create_user(username="prof", email="prof@ecole.cg", password="pwd")
        entry = SyncQueue.objects.create(
            device_id="device-9",
            client_operation_id=uuid.uuid4(),
            user=user,
            operation_type="UPDATE",
            model_name="ecoles.Classe",
            payload={},
        )
        self.assertEqual(str(entry), "[UPDATE] ecoles.Classe — PENDING (device-9)")


class SyncPushViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="directeur", email="directeur@ecole.cg", password="pwd")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse("sync_push")

    def test_requires_authentication(self):
        response = APIClient().post(self.url, {"device_id": "d", "operations": []}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_processes_operations_and_persists_queue_entries(self):
        operation = make_operation()
        response = self.client.post(
            self.url, {"device_id": "device-1", "operations": [operation]}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["details"][0]["status"], "PROCESSED")
        entry = SyncQueue.objects.get(client_operation_id=operation["client_operation_id"])
        self.assertEqual(entry.status, SyncStatus.PROCESSED)
        self.assertEqual(entry.device_id, "device-1")
        self.assertEqual(entry.user, self.user)
        self.assertIsNotNone(entry.processed_at)

    def test_replaying_the_same_operation_is_idempotent(self):
        operation = make_operation()
        payload = {"device_id": "device-1", "operations": [operation]}

        self.client.post(self.url, payload, format="json")
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["processed"], 0)
        self.assertEqual(response.data["details"][0]["status"], "ALREADY_PROCESSED")
        self.assertEqual(SyncQueue.objects.count(), 1)

    def test_rejects_batch_larger_than_fifty_operations(self):
        response = self.client.post(
            self.url,
            {"device_id": "device-1", "operations": [make_operation() for _ in range(51)]},
            format="json",
        )
        # Le sérialiseur refuse déjà les lots > 50 (max_length), avant le garde-fou 413.
        self.assertIn(response.status_code, (400, 413))
        self.assertEqual(SyncQueue.objects.count(), 0)

    def test_rolls_back_whole_batch_when_a_model_is_not_whitelisted(self):
        response = self.client.post(
            self.url,
            {
                "device_id": "device-1",
                "operations": [make_operation(), make_operation(model_name="comptes.User")],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn("comptes.User", response.data["detail"])
        self.assertEqual(SyncQueue.objects.count(), 0)

    def test_invalid_payload_returns_400(self):
        response = self.client.post(
            self.url,
            {"device_id": "device-1", "operations": [make_operation(client_operation_id="nope")]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class SyncStatusViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="directeur", email="directeur@ecole.cg", password="pwd")
        self.other = User.objects.create_user(username="autre", email="autre@ecole.cg", password="pwd")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse("sync_status")

    def _queue(self, user, status_value, **extra):
        return SyncQueue.objects.create(
            device_id="device-1",
            client_operation_id=uuid.uuid4(),
            user=user,
            operation_type="CREATE",
            model_name="ecoles.Ecole",
            payload={},
            status=status_value,
            **extra,
        )

    def test_requires_authentication(self):
        self.assertEqual(APIClient().get(self.url).status_code, 401)

    def test_counts_operations_by_status_for_current_user_only(self):
        self._queue(self.user, SyncStatus.PENDING)
        self._queue(self.user, SyncStatus.PROCESSED, processed_at=timezone.now())
        self._queue(self.user, SyncStatus.CONFLICT, conflict_details={"field": "nom"})
        self._queue(self.other, SyncStatus.PENDING)

        # Le calcul de l'ETag sérialise la réponse avec json.dumps sans encodeur
        # personnalisé : on le neutralise pour pouvoir vérifier le contenu métier.
        with patch("sync.views.json.dumps", return_value="etag-source"):
            response = self.client.get(self.url, HTTP_X_DEVICE_ID="device-42")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pending_count"], 1)
        self.assertEqual(response.data["processed_count"], 1)
        self.assertEqual(response.data["conflict_count"], 1)
        self.assertEqual(response.data["device_id"], "device-42")
        self.assertIsNone(response.data["last_sync"])
        pending = response.data["operations"]["pending"]
        self.assertEqual(len(pending), 1)
        self.assertNotIn("payload", pending[0])

    def test_etag_computation_breaks_when_operations_contain_uuids(self):
        # Bug connu : json.dumps(response_data) ne sait pas sérialiser les UUID /
        # datetime renvoyés par .values(), la vue lève donc une TypeError.
        self._queue(self.user, SyncStatus.PENDING)

        with self.assertRaises(TypeError):
            self.client.get(self.url)

    def test_ignores_operations_processed_more_than_24h_ago(self):
        self._queue(
            self.user,
            SyncStatus.PROCESSED,
            processed_at=timezone.now() - timedelta(hours=25),
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data["processed_count"], 0)

    def test_device_id_defaults_to_unknown_and_pwa_headers_are_set(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["device_id"], "unknown")
        self.assertEqual(response["Cache-Control"], "no-cache, must-revalidate")
        self.assertEqual(response["X-Sync-Version"], "2.0")
        self.assertTrue(response["ETag"].startswith('"'))


class SyncPingViewTests(TestCase):
    def test_ping_is_public_and_returns_server_time(self):
        response = APIClient().get(reverse("sync_ping"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")
        self.assertIn("server_time", response.data)
        self.assertIn("timezone", response.data)


class SyncDeltaViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="directeur", email="directeur@ecole.cg", password="pwd")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse("sync_delta")
        self.ecole = Ecole.objects.create(
            nom="CEG Moungali", code_mepsa="BZV-CEG-001", cycles="COLLEGE", region="Brazzaville"
        )
        self.classe = Classe.objects.create(nom="6ème A", niveau="6EME", ecole=self.ecole)

    def test_requires_authentication(self):
        self.assertEqual(APIClient().get(self.url).status_code, 401)

    def test_returns_active_records_modified_since_last_sync(self):
        inactive = Ecole.objects.create(
            nom="CEG Fermé",
            code_mepsa="BZV-CEG-002",
            cycles="COLLEGE",
            region="Brazzaville",
            is_active=False,
        )

        # comptes.User n'expose pas de champ last_sync : la vue ne peut pas
        # enregistrer la synchronisation, on neutralise donc cette écriture.
        with patch.object(User, "save"):
            response = self.client.get(self.url, {"last_sync": (timezone.now() - timedelta(hours=1)).isoformat()})

        self.assertEqual(response.status_code, 200)
        codes = [e["code_mepsa"] for e in response.data["modified"]["ecoles"]]
        self.assertEqual(codes, [self.ecole.code_mepsa])
        self.assertNotIn(inactive.code_mepsa, codes)
        self.assertEqual(
            [c["nom"] for c in response.data["modified"]["classes"]], [self.classe.nom]
        )
        self.assertIn("delta_since", response.data)

    def test_excludes_records_older_than_the_requested_window(self):
        Ecole.objects.filter(pk=self.ecole.pk).update(updated_at=timezone.now() - timedelta(days=3))
        Classe.objects.filter(pk=self.classe.pk).update(
            updated_at=timezone.now() - timedelta(days=3)
        )

        with patch.object(User, "save"):
            response = self.client.get(
                self.url, {"last_sync": (timezone.now() - timedelta(hours=1)).isoformat()}
            )

        self.assertEqual(response.data["modified"]["ecoles"], [])
        self.assertEqual(response.data["modified"]["classes"], [])


class CleanupSyncQueueDuplicatesCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="directeur", email="directeur@ecole.cg", password="pwd")

    def _queue(self, client_operation_id=None):
        return SyncQueue.objects.create(
            device_id="device-1",
            client_operation_id=client_operation_id or uuid.uuid4(),
            user=self.user,
            operation_type="CREATE",
            model_name="ecoles.Ecole",
            payload={},
        )

    def test_reports_inspected_rows_when_there_is_nothing_to_delete(self):
        self._queue()
        self._queue()
        out = StringIO()

        call_command("cleanup_syncqueue_duplicates", stdout=out)

        self.assertIn("inspected_rows=2", out.getvalue())
        self.assertIn("deleted_rows=0", out.getvalue())
        self.assertEqual(SyncQueue.objects.count(), 2)

    def test_user_id_filter_restricts_the_scope(self):
        self._queue()
        other = User.objects.create_user(username="autre", email="autre@ecole.cg", password="pwd")
        SyncQueue.objects.create(
            device_id="device-2",
            client_operation_id=uuid.uuid4(),
            user=other,
            operation_type="CREATE",
            model_name="ecoles.Ecole",
            payload={},
        )
        out = StringIO()

        call_command("cleanup_syncqueue_duplicates", user_id=self.user.id, stdout=out)

        self.assertIn("inspected_rows=1", out.getvalue())
        self.assertIn(f"user_id={self.user.id}", out.getvalue())

    def test_dry_run_exits_without_deleting(self):
        self._queue()
        out = StringIO()

        with self.assertRaises(SystemExit) as ctx:
            call_command("cleanup_syncqueue_duplicates", dry_run=True, stdout=out)

        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("dry_run=True", out.getvalue())
        self.assertEqual(SyncQueue.objects.count(), 1)
