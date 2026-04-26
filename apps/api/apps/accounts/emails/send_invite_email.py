"""Send the invite email to a prospective tenant member."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.accounts.models import Invite

EXPIRY_HOURS = 24 * 7


def send_invite_email(*, invite: Invite, accept_url: str) -> None:
    """Render templates and dispatch a multipart (text + HTML) email."""
    context = {
        "invite": invite,
        "tenant_name": invite.tenant.name,
        "inviter_email": invite.invited_by.email,
        "accept_url": accept_url,
        "expiry_hours": EXPIRY_HOURS,
    }
    subject = render_to_string(
        "accounts/emails/invite_subject.txt",
        context,
    ).strip()
    text_body = render_to_string("accounts/emails/invite_body.txt", context)
    html_body = render_to_string("accounts/emails/invite_body.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invite.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
