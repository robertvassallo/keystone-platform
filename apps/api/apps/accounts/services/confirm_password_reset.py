"""Service — apply a new password using a reset token."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.accounts.exceptions import InvalidResetToken, WeakPassword
from apps.accounts.models import User


def confirm_password_reset(
    *,
    uidb64: str,
    token: str,
    new_password: str,
) -> User:
    """Validate the reset token and apply the new password.

    Args:
        uidb64: Base64-encoded user PK from the email link.
        token: One-time token issued by ``default_token_generator``.
        new_password: Plaintext new password.

    Returns:
        The updated ``User``.

    Raises:
        InvalidResetToken: Token missing, malformed, expired, or already used
            (the token-generator's hash includes the password, so a successful
            reset invalidates all outstanding tokens).
        WeakPassword: New password fails ``AUTH_PASSWORD_VALIDATORS``.
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise InvalidResetToken("Token does not match a known user.") from exc

    if not default_token_generator.check_token(user, token):
        raise InvalidResetToken("Token is invalid or expired.")

    try:
        validate_password(new_password, user=user)
    except DjangoValidationError as exc:
        raise WeakPassword(list(exc.messages)) from exc

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    return user
