"""Service — create a new user account."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.accounts.exceptions import DuplicateEmail, WeakPassword
from apps.accounts.models import User
from apps.accounts.selectors import get_user_by_email


def sign_up(*, email: str, password: str) -> User:
    """Create a user with the given credentials.

    Args:
        email: The login email; lowercased + stripped before storage.
        password: The plaintext password; hashed via Argon2 inside the
            manager.

    Returns:
        The newly-created ``User``.

    Raises:
        DuplicateEmail: If a non-deleted user with this email already
            exists.
        WeakPassword: If the password fails any rule in
            ``AUTH_PASSWORD_VALIDATORS``.
    """
    normalized = email.lower().strip()

    if get_user_by_email(email=normalized) is not None:
        raise DuplicateEmail(f"Email already registered: {normalized}")

    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise WeakPassword(list(exc.messages)) from exc

    with transaction.atomic():
        return User.objects.create_user(email=normalized, password=password)
