"""Service — update the signed-in user's profile fields."""

from __future__ import annotations

from apps.accounts.models import User

MAX_NAME_LENGTH = 150


def update_profile(
    *,
    user: User,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    """Apply partial updates to the user's profile fields.

    Both arguments are optional. ``None`` means "leave the column
    alone"; an empty string explicitly clears the field. Whitespace is
    trimmed before saving.
    """
    update_fields: list[str] = []

    if first_name is not None:
        user.first_name = first_name.strip()[:MAX_NAME_LENGTH]
        update_fields.append("first_name")

    if last_name is not None:
        user.last_name = last_name.strip()[:MAX_NAME_LENGTH]
        update_fields.append("last_name")

    if update_fields:
        update_fields.append("updated_at")
        user.save(update_fields=update_fields)

    return user
