"""Internal helpers for deriving Account name + slug from an email."""

from __future__ import annotations

import re

from apps.accounts.models import Account

SLUG_FALLBACK = "tenant"


def derive_account_name(email: str) -> str:
    """Return a friendly Account name derived from an email."""
    local = email.split("@", maxsplit=1)[0] or "Tenant"
    return f"{local}'s account"


def derive_account_slug(email: str) -> str:
    """Return a URL-safe slug derived from the email's local part."""
    local = email.split("@", maxsplit=1)[0].lower()
    sanitized = re.sub(r"[^a-z0-9]+", "-", local).strip("-")
    return sanitized or SLUG_FALLBACK


def unique_slug(base: str) -> str:
    """Find a free slug, suffixing ``-2``, ``-3``, ... on collision."""
    candidate = base
    suffix = 2
    while Account.objects.filter(slug=candidate).exists():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
