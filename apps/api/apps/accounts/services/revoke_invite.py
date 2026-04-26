"""Service — mark a pending invite as revoked."""

from __future__ import annotations

from django.utils import timezone

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.exceptions import InvalidInviteState
from apps.accounts.models import Invite, User

from .record_audit_event import record_audit_event


def revoke_invite(
    *,
    invite: Invite,
    revoked_by: User,
    audit_context: AuditContext | None = None,
) -> Invite:
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

    record_audit_event(
        tenant=invite.tenant,
        action=AuditAction.INVITE_REVOKED,
        context=audit_context,
        target_id=invite.pk,
        target_type="invite",
        target_label=invite.email,
    )
    return invite
