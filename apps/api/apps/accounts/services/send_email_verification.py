"""Service — issue a verification link and email it to the user."""

from __future__ import annotations

from urllib.parse import urlencode

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.emails import send_email_verification_email
from apps.accounts.models import User

from ._email_verification_token import email_verification_token_generator


def send_email_verification(*, user: User) -> None:
    """Generate a fresh token + email it.

    Idempotent at the user level — calling twice issues two valid tokens
    until the first is used (or both expire). Already-verified users get
    a link that succeeds-as-noop on click; we don't gate the send because
    a user may be verifying a second device, troubleshooting, etc.
    """
    if not user.is_active:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)
    query = urlencode({"uid": uidb64, "token": token})
    verify_url = f"{settings.FRONTEND_URL}/verify-email?{query}"

    send_email_verification_email(user=user, verify_url=verify_url)
