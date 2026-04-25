"""Create the Account model + reuse the set_updated_at trigger."""

from __future__ import annotations

import apps.accounts.models._uuid
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

CREATE_ACCOUNTS_TRIGGER = """
DROP TRIGGER IF EXISTS set_accounts_updated_at ON accounts;
CREATE TRIGGER set_accounts_updated_at
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
"""

DROP_ACCOUNTS_TRIGGER = "DROP TRIGGER IF EXISTS set_accounts_updated_at ON accounts;"


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_mfarecoverycode"),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=apps.accounts.models._uuid.uuid_v7,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "slug",
                    models.SlugField(
                        help_text=(
                            "Lowercase URL-safe identifier; unique among non-deleted accounts."
                        ),
                        max_length=100,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "deleted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_deleted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "accounts",
                "ordering": ["-created_at"],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("deleted_at__isnull", True)),
                        fields=("slug",),
                        name="uq_accounts_slug_active",
                    ),
                ],
            },
        ),
        migrations.RunSQL(
            sql=CREATE_ACCOUNTS_TRIGGER,
            reverse_sql=DROP_ACCOUNTS_TRIGGER,
        ),
    ]
