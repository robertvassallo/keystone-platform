"""Helper — build an ``AuditContext`` from a DRF request."""

from __future__ import annotations

from rest_framework.request import Request

from apps.accounts.audit import AuditContext
from apps.accounts.models import User


def audit_context_from_request(
    request: Request,
    *,
    actor: User | None = None,
) -> AuditContext:
    """Capture actor / IP / user-agent from a request.

    ``actor`` defaults to ``request.user`` when authenticated; pass it
    explicitly for flows where ``request.user`` is anonymous but the
    actor is known (e.g. password-reset confirm, invite-accept).
    """
    if actor is None:
        candidate = getattr(request, "user", None)
        if isinstance(candidate, User):
            actor = candidate

    return AuditContext(
        actor=actor,
        ip=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )


def _client_ip(request: Request) -> str | None:
    """Return the most-likely client IP, honoring a single X-Forwarded-For hop."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        # First entry is the originating client (per the spec).
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None
