"""Service — consume an invite token + create the new User in its tenant."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.exceptions import (
    DuplicateEmail,
    InvalidInviteToken,
    WeakPassword,
)
from apps.accounts.models import User
from apps.accounts.selectors import get_user_by_email

from .preview_invite import preview_invite
from .record_audit_event import record_audit_event


def accept_invite(
    *,
    uidb64: str,
    token: str,
    password: str,
    audit_context: AuditContext | None = None,
) -> User:
    """Validate the invite token and create a User in the invite's tenant.

    Raises:
        InvalidInviteToken: As ``preview_invite``.
        DuplicateEmail: A User with this email was created between the
            invite being sent and accepted.
        WeakPassword: New password fails ``AUTH_PASSWORD_VALIDATORS``.
    """
    invite = preview_invite(uidb64=uidb64, token=token)

    if get_user_by_email(email=invite.email) is not None:
        # Closes a TOCTOU window between send-invite and accept.
        raise DuplicateEmail(
            f"An account with email {invite.email} already exists.",
        )

    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise WeakPassword(list(exc.messages)) from exc

    with transaction.atomic():
        # Re-check inside the transaction; if the invite was concurrently
        # accepted or revoked, fail loudly.
        invite.refresh_from_db()
        if invite.accepted_at is not None or invite.revoked_at is not None:
            raise InvalidInviteToken("Invite is no longer valid.")

        user = User.objects.create_user(
            email=invite.email,
            password=password,
            tenant=invite.tenant,
        )
        invite.accepted_at = timezone.now()
        invite.accepted_by = user
        invite.save(update_fields=["accepted_at", "accepted_by", "updated_at"])

    bound_context = AuditContext(
        actor=user,
        ip=audit_context.ip if audit_context is not None else None,
        user_agent=audit_context.user_agent if audit_context is not None else None,
    )
    record_audit_event(
        tenant=invite.tenant,
        action=AuditAction.INVITE_ACCEPTED,
        context=bound_context,
        target_id=invite.pk,
        target_type="invite",
        target_label=invite.email,
    )

    return user
