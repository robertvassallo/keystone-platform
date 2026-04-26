"""Service — mark a pending invite as revoked."""

from __future__ import annotations

from django.utils import timezone

from apps.accounts.exceptions import InvalidInviteState
from apps.accounts.models import Invite, User


def revoke_invite(*, invite: Invite, revoked_by: User) -> Invite:
    """Set ``revoked_at`` on the invite. No-op friendly re-revoke is rejected.

    Raises:
        InvalidInviteState: Invite is already accepted or revoked.
    """
    if invite.accepted_at is not None:
        raise InvalidInviteState("Cannot revoke an already-accepted invite.")
    if invite.revoked_at is not None:
        raise InvalidInviteState("Invite is already revoked.")

    invite.revoked_at = timezone.now()
    invite.revoked_by = revoked_by
    invite.save(update_fields=["revoked_at", "revoked_by", "updated_at"])
    return invite
