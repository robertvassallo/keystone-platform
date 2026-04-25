"""Selector — fetch a single user by primary key, scoped to a tenant."""

from __future__ import annotations

from uuid import UUID

from apps.accounts.models import User


def get_user_by_id(*, user_id: UUID, tenant_id: UUID) -> User | None:
    """Return the active user with this id within ``tenant_id``, or ``None``.

    The default manager already filters soft-deleted rows; the
    ``tenant_id`` filter then enforces isolation. Cross-tenant lookups
    return ``None`` — the view layer renders that as a 404 (same as
    "never existed") so cross-tenant existence isn't leaked.
    """
    return User.objects.filter(pk=user_id, tenant_id=tenant_id).first()
