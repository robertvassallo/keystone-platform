"""Data migration — grandfather every existing User as verified.

Pre-existing users were created (or seeded) by an admin before email
verification existed; treating them as unverified would flood the
banner UI and lock no value. Backfill sets ``email_verified_at =
created_at`` for every row where it's currently null. From this PR on,
only fresh sign-ups land with ``email_verified_at IS NULL``.

Reverses by setting ``email_verified_at = NULL`` on every row — the
column itself goes away when ``0006`` reverses.
"""

from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import F


def forward(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model("accounts", "User")  # noqa: N806
    User.objects.filter(email_verified_at__isnull=True).update(
        email_verified_at=F("created_at"),
    )


def reverse(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model("accounts", "User")  # noqa: N806
    User.objects.update(email_verified_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_email_verified_at"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
