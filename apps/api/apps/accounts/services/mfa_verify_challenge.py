"""Service — verify a partial-auth ticket and complete sign-in."""

from __future__ import annotations

from datetime import datetime

from django.conf import settings
from django.contrib.auth import login as django_login
from django.http import HttpRequest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import InvalidMFACode, MFAChallengeExpired
from apps.accounts.models import User

from ._mfa_helpers import consume_recovery_code, is_totp_format

CHALLENGE_SESSION_KEY = "mfa_challenge"


def verify_mfa_challenge(*, request: HttpRequest, code: str) -> User:
    """Validate the partial ticket + the supplied code, complete sign-in.

    The ticket is **consumed** (removed from session) on success so it
    can't be replayed. On a wrong code the ticket is left in place so the
    user can retry within the TTL window. On any other failure path
    (missing / expired / unknown user) the ticket is removed.

    Raises:
        MFAChallengeExpired: No ticket is present in the session, the
            ticket is past ``expires_at``, or the referenced user no
            longer exists.
        InvalidMFACode: The supplied code did not validate.
    """
    ticket = request.session.get(CHALLENGE_SESSION_KEY)
    if not isinstance(ticket, dict):
        raise MFAChallengeExpired("No active sign-in challenge.")

    expires_at_iso = ticket.get("expires_at", "")
    user_id = ticket.get("user_id", "")
    remember_me = bool(ticket.get("remember_me", False))

    try:
        expires_at = datetime.fromisoformat(expires_at_iso)
    except (TypeError, ValueError) as exc:
        request.session.pop(CHALLENGE_SESSION_KEY, None)
        raise MFAChallengeExpired("Sign-in challenge is malformed.") from exc

    from django.utils import timezone  # noqa: PLC0415 — avoid module-load order

    if timezone.now() >= expires_at:
        request.session.pop(CHALLENGE_SESSION_KEY, None)
        raise MFAChallengeExpired("Sign-in challenge has expired.")

    user = User.objects.filter(pk=user_id).first()
    if user is None or not user.is_active:
        request.session.pop(CHALLENGE_SESSION_KEY, None)
        raise MFAChallengeExpired("Sign-in challenge no longer matches a user.")

    if _verify_code(user=user, code=code):
        request.session.pop(CHALLENGE_SESSION_KEY, None)
        django_login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        if remember_me:
            request.session.set_expiry(settings.REMEMBER_ME_DURATION)
        return user

    raise InvalidMFACode("Invalid authentication code.")


def _verify_code(*, user: User, code: str) -> bool:
    """Return True if ``code`` is a valid TOTP for any device or a fresh recovery code."""
    if is_totp_format(code):
        for device in TOTPDevice.objects.filter(user=user, confirmed=True):
            if device.verify_token(code):
                return True
        return False
    return consume_recovery_code(user=user, code=code)
