"""Service — authenticate and start a session."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.http import HttpRequest

from apps.accounts.exceptions import InvalidCredentials
from apps.accounts.models import User


def sign_in(
    *,
    request: HttpRequest,
    email: str,
    password: str,
    remember_me: bool,
) -> User:
    """Authenticate the credentials, start a Django session.

    Args:
        request: The HTTP request — Django binds the session to it.
        email: Login email.
        password: Plaintext password.
        remember_me: If True, extend session expiry to
            ``settings.REMEMBER_ME_DURATION``; otherwise the session ends
            on browser close.

    Returns:
        The authenticated ``User``.

    Raises:
        InvalidCredentials: If authentication fails for any reason
            (wrong password, unknown email, inactive account).
    """
    user = django_authenticate(
        request,
        username=email.lower().strip(),
        password=password,
    )
    if user is None or not isinstance(user, User):
        raise InvalidCredentials("Email or password is incorrect.")

    django_login(request, user)

    if remember_me:
        request.session.set_expiry(settings.REMEMBER_ME_DURATION)

    return user
