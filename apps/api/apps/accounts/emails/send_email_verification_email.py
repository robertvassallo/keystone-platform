"""Send the email-verification email."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.accounts.models import User

EXPIRY_HOURS = 24


def send_email_verification_email(*, user: User, verify_url: str) -> None:
    """Render templates and dispatch a multipart (text + HTML) email."""
    context = {
        "user": user,
        "verify_url": verify_url,
        "expiry_hours": EXPIRY_HOURS,
    }
    subject = render_to_string(
        "accounts/emails/email_verification_subject.txt",
        context,
    ).strip()
    text_body = render_to_string(
        "accounts/emails/email_verification_body.txt",
        context,
    )
    html_body = render_to_string(
        "accounts/emails/email_verification_body.html",
        context,
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
