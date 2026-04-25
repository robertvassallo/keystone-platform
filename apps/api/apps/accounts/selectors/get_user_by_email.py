"""Selector — fetch a user by email."""

from __future__ import annotations

from apps.accounts.models import User


def get_user_by_email(*, email: str) -> User | None:
    """Return the active user with this email, or ``None`` if absent.

    Email lookup is case-insensitive (the column is normalised to
    lowercase on write); soft-deleted rows are excluded by the default
    manager.
    """
    return User.objects.filter(email=email.lower().strip()).first()
