"""Service — change a signed-in user's password."""

from __future__ import annotations

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest

from apps.accounts.exceptions import WeakPassword, WrongCurrentPassword
from apps.accounts.models import User


def change_password(
    *,
    request: HttpRequest,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """Verify the current password, validate + save the new one.

    The current session's auth hash is rotated via
    ``update_session_auth_hash`` so the user stays signed in *here*; every
    other session for this user is invalidated implicitly because Django
    ties session validity to the password hash.
    """
    if not user.check_password(current_password):
        raise WrongCurrentPassword("Current password is incorrect.")

    try:
        validate_password(new_password, user=user)
    except DjangoValidationError as exc:
        raise WeakPassword(list(exc.messages)) from exc

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    update_session_auth_hash(request, user)
