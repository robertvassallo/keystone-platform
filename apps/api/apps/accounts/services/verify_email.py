"""Service — consume a verification token and mark the user verified."""

from __future__ import annotations

from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.accounts.exceptions import InvalidVerificationToken
from apps.accounts.models import User

from ._email_verification_token import email_verification_token_generator


def verify_email(*, uidb64: str, token: str) -> User:
    """Validate the token and stamp ``email_verified_at`` on the user.

    Already-verified users return successfully without re-stamping —
    the link survives a double-click without raising.

    Args:
        uidb64: Base64-encoded user PK from the email link.
        token: One-time token issued by ``email_verification_token_generator``.

    Returns:
        The (possibly already-verified) ``User`` row.

    Raises:
        InvalidVerificationToken: Token missing, malformed, expired, or
            from a user whose state has changed since the token was issued.
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise InvalidVerificationToken("Token does not match a known user.") from exc

    if not email_verification_token_generator.check_token(user, token):
        raise InvalidVerificationToken("Token is invalid or expired.")

    if user.email_verified_at is None:
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email_verified_at", "updated_at"])

    return user
