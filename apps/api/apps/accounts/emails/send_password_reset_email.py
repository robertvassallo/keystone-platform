"""Send the password-reset email."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.accounts.models import User

EXPIRY_HOURS = 1


def send_password_reset_email(*, user: User, reset_url: str) -> None:
    """Render templates and dispatch a multipart (text + HTML) email."""
    context = {
        "user": user,
        "reset_url": reset_url,
        "expiry_hours": EXPIRY_HOURS,
    }
    subject = render_to_string(
        "accounts/emails/password_reset_subject.txt",
        context,
    ).strip()
    text_body = render_to_string("accounts/emails/password_reset_body.txt", context)
    html_body = render_to_string("accounts/emails/password_reset_body.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
