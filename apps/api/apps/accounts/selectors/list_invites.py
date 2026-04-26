"""Selector — read-only list of invites for one tenant."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.models import Invite


class InviteStatus(StrEnum):
    """Mutually-exclusive status filter for the invites list."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


def list_invites(
    *,
    tenant_id: UUID,
    status: InviteStatus | None = None,
) -> list[Invite]:
    """Return invites for ``tenant_id``, newest first.

    Args:
        tenant_id: Required tenant scope; cross-tenant rows are excluded.
        status: Optional filter:
            ``PENDING`` → not accepted, not revoked, not expired
            ``ACCEPTED`` → accepted_at is set
            ``REVOKED`` → revoked_at is set
            ``EXPIRED`` → not accepted, not revoked, expires_at <= now
            ``None`` → no filter (all invites for this tenant)
    """
    queryset: QuerySet[Invite] = Invite.objects.filter(tenant_id=tenant_id)

    now = timezone.now()
    if status is InviteStatus.PENDING:
        queryset = queryset.filter(
            accepted_at__isnull=True,
            revoked_at__isnull=True,
            expires_at__gt=now,
        )
    elif status is InviteStatus.ACCEPTED:
        queryset = queryset.filter(accepted_at__isnull=False)
    elif status is InviteStatus.REVOKED:
        queryset = queryset.filter(revoked_at__isnull=False)
    elif status is InviteStatus.EXPIRED:
        queryset = queryset.filter(
            accepted_at__isnull=True,
            revoked_at__isnull=True,
            expires_at__lte=now,
        )

    return list(
        queryset.order_by("-created_at", "-id").select_related("invited_by"),
    )


def get_pending_invite_count(*, tenant_id: UUID) -> int:
    """Return the count of pending invites for a tenant."""
    now = timezone.now()
    return Invite.objects.filter(
        Q(tenant_id=tenant_id)
        & Q(accepted_at__isnull=True)
        & Q(revoked_at__isnull=True)
        & Q(expires_at__gt=now),
    ).count()
