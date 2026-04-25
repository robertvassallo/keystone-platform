"""Selector — paginated read-only list of users, scoped to a tenant."""

from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
MIN_PAGE = 1


def list_users(
    *,
    tenant_id: UUID,
    page: int = MIN_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> tuple[list[User], int]:
    """Return (rows, total_count) for the given page, scoped to ``tenant_id``.

    Args:
        tenant_id: The tenant whose users to return. Cross-tenant rows
            are excluded; this is the only tenant-isolation gate.
        page: 1-indexed page. Values < 1 are clamped to 1.
        page_size: Rows per page. Clamped to [1, MAX_PAGE_SIZE].

    Returns:
        Tuple of the page's rows and the unfiltered total count
        (within the tenant). Sort is fixed to ``-created_at`` (newest
        first); soft-deleted users are excluded by the default manager.
    """
    safe_page = max(page, MIN_PAGE)
    safe_page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    queryset: QuerySet[User] = (
        User.objects.filter(tenant_id=tenant_id)
        .only(
            "id",
            "email",
            "is_active",
            "is_staff",
            "created_at",
            "last_login",
        )
        .order_by("-created_at", "-id")
    )

    total = queryset.count()
    offset = (safe_page - MIN_PAGE) * safe_page_size
    rows = list(queryset[offset : offset + safe_page_size])

    return rows, total
