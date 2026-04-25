"""Service — end the current session."""

from __future__ import annotations

from django.contrib.auth import logout as django_logout
from django.http import HttpRequest


def sign_out(*, request: HttpRequest) -> None:
    """End the current session. Idempotent — safe to call when not logged in."""
    django_logout(request)
