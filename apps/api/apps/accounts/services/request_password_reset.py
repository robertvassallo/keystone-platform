"""Service — initiate a password reset by email."""

from __future__ import annotations

from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.emails import send_password_reset_email
from apps.accounts.selectors import get_user_by_email


def request_password_reset(*, email: str) -> None:
    """Send a password-reset email if the address is registered.

    Always returns ``None`` — no signal whether the email matched. This is
    deliberate to prevent account-enumeration via this endpoint.
    """
    user = get_user_by_email(email=email)
    if user is None or not user.is_active:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    query = urlencode({"uid": uidb64, "token": token})
    reset_url = f"{settings.FRONTEND_URL}/reset-password?{query}"

    send_password_reset_email(user=user, reset_url=reset_url)
