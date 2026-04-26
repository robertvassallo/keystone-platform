"""Service — write a single immutable audit event row."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.models import Account, AuditEvent

MAX_USER_AGENT_LENGTH = 500


def record_audit_event(  # noqa: PLR0913 — keyword-only call site keeps it readable
    *,
    tenant: Account,
    action: AuditAction,
    context: AuditContext | None = None,
    target_id: UUID | None = None,
    target_type: str = "",
    target_label: str = "",
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Append one audit row.

    The actor's email is snapshotted from ``context.actor`` at write time so
    the row stays readable after the actor is removed. ``user_agent`` is
    truncated to the column's max length to keep noisy headers from blowing
    up the row.
    """
    actor = context.actor if context is not None else None
    ip = context.ip if context is not None else None
    user_agent = context.user_agent if context is not None else None

    return AuditEvent.objects.create(
        tenant=tenant,
        actor=actor,
        actor_email=actor.email if actor is not None else "",
        action=str(action),
        target_id=target_id,
        target_type=target_type,
        target_label=target_label,
        metadata=metadata or {},
        ip=ip,
        user_agent=(user_agent or "")[:MAX_USER_AGENT_LENGTH],
    )
