"""Service — look up an invite by uid + plaintext token (read-only)."""

from __future__ import annotations

from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.accounts.exceptions import InvalidInviteToken
from apps.accounts.models import Invite

from ._invite_token import hash_invite_token


def preview_invite(*, uidb64: str, token: str) -> Invite:
    """Validate uid + token and return the (still-pending) Invite.

    Raises:
        InvalidInviteToken: Token missing, malformed, expired,
            already-accepted, or revoked.
    """
    try:
        invite_id = force_str(urlsafe_base64_decode(uidb64))
        invite = Invite.objects.select_related("tenant").get(pk=invite_id)
    except (TypeError, ValueError, OverflowError, Invite.DoesNotExist) as exc:
        raise InvalidInviteToken("Invite link does not match a known invite.") from exc

    if invite.token_hash != hash_invite_token(token):
        raise InvalidInviteToken("Invite token is invalid.")

    if invite.accepted_at is not None:
        raise InvalidInviteToken("Invite has already been used.")

    if invite.revoked_at is not None:
        raise InvalidInviteToken("Invite has been revoked.")

    if invite.expires_at <= timezone.now():
        raise InvalidInviteToken("Invite has expired.")

    return invite
