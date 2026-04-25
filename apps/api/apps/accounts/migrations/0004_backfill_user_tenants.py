"""Data migration — give every existing User its own Account.

Each user becomes the sole member of a freshly-created tenant, with the
slug derived from their email's local part. On reverse, we clear the
``tenant_id`` and drop every Account (this whole feature is one-shot).
"""

from __future__ import annotations

import re

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

SLUG_FALLBACK = "tenant"


def _slug_from_email(email: str) -> str:
    local = email.split("@")[0].lower()
    sanitized = re.sub(r"[^a-z0-9]+", "-", local).strip("-")
    return sanitized or SLUG_FALLBACK


def forward(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model("accounts", "User")  # noqa: N806
    Account = apps.get_model("accounts", "Account")  # noqa: N806

    used_slugs: set[str] = set(Account.objects.values_list("slug", flat=True))

    for user in User.objects.filter(tenant_id__isnull=True).order_by("created_at"):
        base_slug = _slug_from_email(user.email)
        candidate = base_slug
        suffix = 2
        while candidate in used_slugs:
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        used_slugs.add(candidate)

        local_part = user.email.split("@")[0] or "Tenant"
        account = Account.objects.create(
            name=f"{local_part}'s account",
            slug=candidate,
        )
        user.tenant_id = account.pk
        user.save(update_fields=["tenant_id", "updated_at"])


def reverse(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model("accounts", "User")  # noqa: N806
    Account = apps.get_model("accounts", "Account")  # noqa: N806

    User.objects.update(tenant_id=None)
    Account.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_account"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
