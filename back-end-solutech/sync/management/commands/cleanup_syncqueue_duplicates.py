import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from sync.models import SyncQueue


class Command(BaseCommand):
    help = "Nettoie les doublons fonctionnels dans SyncQueue (garde la plus récente par client_operation_id)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule le nettoyage sans supprimer de lignes.",
        )
        parser.add_argument(
            "--keep",
            choices=["latest", "earliest"],
            default="latest",
            help="Quelle entrée garder pour chaque client_operation_id.",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=None,
            help="Limite le nettoyage à un user donné (optionnel).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        keep = options["keep"]
        user_id = options["user_id"]

        order = "-created_at" if keep == "latest" else "created_at"

        qs = SyncQueue.objects.all()
        if user_id is not None:
            qs = qs.filter(user_id=user_id)

        # Important: client_operation_id est unique=True, donc en base un vrai doublon
        # (même client_operation_id) ne devrait pas exister. Ce nettoyage sert de garde
        # (ex: DB déjà corrompue, ou anomalies selon migrations antérieures).
        # Stratégie: regrouper par client_operation_id et conserver 1 ligne, supprimer le reste.

        # On utilise une approche itérative pour rester compatible sqlite.
        client_ids = (
            qs.values_list("client_operation_id", flat=True)
            .distinct()
        )

        deleted_total = 0
        inspected_total = 0

        with transaction.atomic():
            for client_id in client_ids:
                rows = list(
                    qs.filter(client_operation_id=client_id).order_by(order, "id")
                )
                inspected_total += len(rows)
                if len(rows) <= 1:
                    continue

                # garder la première selon l'ordre
                to_keep = rows[0]
                to_delete = rows[1:]

                if not dry_run:
                    SyncQueue.objects.filter(id__in=[r.id for r in to_delete]).delete()

                deleted_total += len(to_delete)

                self.stdout.write(
                    f"client_operation_id={client_id} kept={to_keep.id} delete_count={len(to_delete)}"
                )

        self.stdout.write(
            f"Done. inspected_rows={inspected_total} deleted_rows={deleted_total} dry_run={dry_run} keep={keep} user_id={user_id}"
        )

        if dry_run:
            sys.exit(0)

