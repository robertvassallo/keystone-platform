"""Service — authenticate and either start a session or issue an MFA challenge."""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.http import HttpRequest
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import InvalidCredentials
from apps.accounts.models import User

from .mfa_verify_challenge import CHALLENGE_SESSION_KEY

# Partial-auth ticket TTL — see decisions-log for rationale.
MFA_CHALLENGE_TTL = timedelta(minutes=5)


def sign_in(
    *,
    request: HttpRequest,
    email: str,
    password: str,
    remember_me: bool,
) -> User | None:
    """Authenticate; either complete the sign-in or queue an MFA challenge.

    Args:
        request: The HTTP request — Django binds the session to it.
        email: Login email.
        password: Plaintext password.
        remember_me: If True, extend session expiry to
            ``settings.REMEMBER_ME_DURATION`` after sign-in completes
            (whether immediately or after MFA verify).

    Returns:
        The authenticated ``User`` if sign-in completed; ``None`` if the
        user has MFA enabled and a partial-auth ticket has been stashed
        in the session for ``mfa_verify_challenge`` to consume.

    Raises:
        InvalidCredentials: Authentication failed for any reason.
    """
    user = django_authenticate(
        request,
        username=email.lower().strip(),
        password=password,
    )
    if user is None or not isinstance(user, User):
        raise InvalidCredentials("Email or password is incorrect.")

    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        request.session[CHALLENGE_SESSION_KEY] = {
            "user_id": str(user.pk),
            "remember_me": remember_me,
            "expires_at": (timezone.now() + MFA_CHALLENGE_TTL).isoformat(),
        }
        return None

    django_login(request, user)
    if remember_me:
        request.session.set_expiry(settings.REMEMBER_ME_DURATION)
    return user
