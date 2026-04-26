"""Service — update the signed-in user's tenant (rename + reslug)."""

from __future__ import annotations

import re

from apps.accounts.exceptions import DuplicateSlug, InvalidSlug
from apps.accounts.models import Account

MAX_NAME_LENGTH = 200
MAX_SLUG_LENGTH = 100
SLUG_REGEX = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def update_tenant(
    *,
    tenant: Account,
    name: str | None = None,
    slug: str | None = None,
) -> Account:
    """Apply partial updates to ``tenant``'s name and/or slug.

    Both arguments are optional. ``None`` leaves the column alone; an
    empty / whitespace-only value is rejected (a tenant can't have a
    blank name or slug). Trimmed before saving.

    Raises:
        InvalidSlug: ``slug`` doesn't match the slug regex (the same
            shape sign-up auto-derives).
        DuplicateSlug: ``slug`` is taken by another non-deleted tenant.
    """
    update_fields: list[str] = []

    if name is not None:
        trimmed = name.strip()[:MAX_NAME_LENGTH]
        if not trimmed:
            raise InvalidSlug("Tenant name cannot be empty.")
        tenant.name = trimmed
        update_fields.append("name")

    if slug is not None:
        normalized = slug.strip().lower()[:MAX_SLUG_LENGTH]
        if not SLUG_REGEX.match(normalized):
            raise InvalidSlug(
                "Slug must be lowercase letters, digits, or hyphens, "
                "and may not start or end with a hyphen.",
            )
        if normalized != tenant.slug:
            collision = (
                Account.objects.filter(
                    slug=normalized,
                    deleted_at__isnull=True,
                )
                .exclude(pk=tenant.pk)
                .exists()
            )
            if collision:
                raise DuplicateSlug(f"The slug {normalized!r} is already taken.")
        tenant.slug = normalized
        update_fields.append("slug")

    if update_fields:
        update_fields.append("updated_at")
        tenant.save(update_fields=update_fields)

    return tenant
