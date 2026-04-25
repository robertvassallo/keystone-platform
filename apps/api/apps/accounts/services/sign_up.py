"""Service — create a new user account *and its tenant*."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.accounts.exceptions import DuplicateEmail, WeakPassword
from apps.accounts.models import Account, User
from apps.accounts.selectors import get_user_by_email

from ._account_naming import (
    derive_account_name,
    derive_account_slug,
    unique_slug,
)


def sign_up(*, email: str, password: str) -> User:
    """Create a user, the tenant they belong to, and return the user.

    A fresh ``Account`` is created in the same transaction; the new
    ``User.tenant`` FK points at it. Tenant invite / membership flows
    will replace the auto-create path later.

    Args:
        email: Login email; lowercased + stripped before storage.
        password: Plaintext password; hashed via Argon2 in the manager.

    Returns:
        The newly-created ``User`` (with ``user.tenant`` populated).

    Raises:
        DuplicateEmail: If a non-deleted user with this email already
            exists.
        WeakPassword: If the password fails ``AUTH_PASSWORD_VALIDATORS``.
    """
    normalized = email.lower().strip()

    if get_user_by_email(email=normalized) is not None:
        raise DuplicateEmail(f"Email already registered: {normalized}")

    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise WeakPassword(list(exc.messages)) from exc

    with transaction.atomic():
        account = Account.objects.create(
            name=derive_account_name(normalized),
            slug=unique_slug(derive_account_slug(normalized)),
        )
        return User.objects.create_user(
            email=normalized,
            password=password,
            tenant=account,
        )
