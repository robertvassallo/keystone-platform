"""Selector — fetch a single user by primary key."""

from __future__ import annotations

from uuid import UUID

from apps.accounts.models import User


def get_user_by_id(*, user_id: UUID) -> User | None:
    """Return the active user with this id, or ``None`` if absent.

    The default manager already filters soft-deleted rows; callers see
    ``None`` for unknown ids and for users whose ``deleted_at`` is set.
    The view layer renders both as 404 to avoid leaking which case it is.
    """
    return User.objects.filter(pk=user_id).first()
