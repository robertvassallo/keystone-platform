"""``AuditContext`` — request-side data passed from views to services.

Views build an ``AuditContext`` from ``request`` (actor, IP, user-agent)
and pass it through to the service layer. Services pass it on to
``record_audit_event``. Optional everywhere — services that don't have
a request context (cron jobs, management commands) call with ``None``
and the resulting audit row carries blank IP / user-agent.
"""

from __future__ import annotations

from dataclasses import dataclass

from apps.accounts.models import User


@dataclass(frozen=True, slots=True)
class AuditContext:
    """Identity + transport metadata for an audit event."""

    actor: User | None = None
    ip: str | None = None
    user_agent: str | None = None
