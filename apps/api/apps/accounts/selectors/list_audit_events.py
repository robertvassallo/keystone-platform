"""Selector — paginated read of audit events for one tenant."""

from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import AuditEvent

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
MIN_PAGE = 1


def list_audit_events(
    *,
    tenant_id: UUID,
    page: int = MIN_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> tuple[list[AuditEvent], int]:
    """Return ``(rows, total)`` for the tenant's audit log, newest first.

    Sort is fixed (``-created_at, -id``) because the result table only
    makes sense in chronological order. Filters / search land in a
    follow-up.
    """
    safe_page = max(page, MIN_PAGE)
    safe_page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    queryset: QuerySet[AuditEvent] = AuditEvent.objects.filter(
        tenant_id=tenant_id,
    ).only(
        "id",
        "actor_email",
        "action",
        "target_label",
        "target_type",
        "ip",
        "created_at",
    ).order_by("-created_at", "-id")

    total = queryset.count()
    offset = (safe_page - MIN_PAGE) * safe_page_size
    rows = list(queryset[offset : offset + safe_page_size])
    return rows, total
