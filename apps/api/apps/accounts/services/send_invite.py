"""Service — create an Invite + email it to the recipient."""

from __future__ import annotations

from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.emails import send_invite_email
from apps.accounts.exceptions import (
    DuplicateInvite,
    DuplicateMember,
)
from apps.accounts.models import Account, Invite, User
from apps.accounts.selectors import get_user_by_email

from ._invite_token import generate_invite_token, hash_invite_token


def send_invite(*, tenant: Account, email: str, invited_by: User) -> Invite:
    """Create a pending invite + send the email.

    Raises:
        DuplicateMember: An active user with this email already belongs
            to a tenant (the invite would be a no-op or worse, a tenant
            grab).
        DuplicateInvite: A pending invite for this ``(tenant, email)``
            already exists. Caller can revoke + resend if intent was
            to refresh.
    """
    normalized = email.lower().strip()

    existing_user = get_user_by_email(email=normalized)
    if existing_user is not None:
        raise DuplicateMember(
            f"A user with email {normalized} already exists.",
        )

    pending_exists = Invite.objects.filter(
        tenant=tenant,
        email=normalized,
        accepted_at__isnull=True,
        revoked_at__isnull=True,
    ).exists()
    if pending_exists:
        raise DuplicateInvite(
            f"A pending invite for {normalized} already exists.",
        )

    plaintext = generate_invite_token()
    invite = Invite.objects.create(
        tenant=tenant,
        email=normalized,
        invited_by=invited_by,
        token_hash=hash_invite_token(plaintext),
    )

    uidb64 = urlsafe_base64_encode(force_bytes(invite.pk))
    query = urlencode({"uid": uidb64, "token": plaintext})
    accept_url = f"{settings.FRONTEND_URL}/accept-invite?{query}"

    transaction.on_commit(
        lambda: send_invite_email(invite=invite, accept_url=accept_url),
    )

    return invite
