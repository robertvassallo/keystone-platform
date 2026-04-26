"""Data migration — set Account.owner for existing tenants.

Pre-existing accounts have exactly one User (the sign-up auto-create
path created one user per tenant). Pick that User as the owner. The
``owner`` column stays nullable at the DB layer so future sign-ups can
insert the Account row before the User exists; the application layer
keeps it set thereafter.

Reverses by clearing every ``Account.owner`` — the column itself goes
away when ``0009`` reverses.
"""

from __future__ import annotations

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forward(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Account = apps.get_model("accounts", "Account")  # noqa: N806

    for account in Account.objects.filter(owner__isnull=True):
        first_user = account.users.order_by("created_at").first()
        if first_user is not None:
            account.owner = first_user
            account.save(update_fields=["owner", "updated_at"])


def reverse(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Account = apps.get_model("accounts", "Account")  # noqa: N806
    Account.objects.update(owner=None)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_account_owner_and_invite"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
