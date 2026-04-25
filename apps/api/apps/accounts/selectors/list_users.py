"""Selector — paginated read-only list of users, scoped to a tenant."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
MIN_PAGE = 1
MAX_QUERY_LENGTH = 200


class UserStatus(StrEnum):
    """Mutually-exclusive filter values for the users list."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    STAFF = "staff"


def list_users(
    *,
    tenant_id: UUID,
    page: int = MIN_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    status: UserStatus | None = None,
) -> tuple[list[User], int]:
    """Return (rows, total_count) for the given page, scoped to ``tenant_id``.

    Args:
        tenant_id: The tenant whose users to return. Cross-tenant rows
            are excluded; this is the only tenant-isolation gate.
        page: 1-indexed page. Values < 1 are clamped to 1.
        page_size: Rows per page. Clamped to [1, MAX_PAGE_SIZE].
        q: Optional case-insensitive substring match against ``email``.
            Whitespace-only or empty strings are ignored. Trimmed to
            ``MAX_QUERY_LENGTH``.
        status: Optional filter:
            ``ACTIVE`` → ``is_active=True``; ``INACTIVE`` → ``is_active=False``;
            ``STAFF`` → ``is_staff=True``. ``None`` applies no filter.

    Returns:
        Tuple of the page's rows and the filter-aware total count
        (within the tenant). Sort is fixed to ``-created_at`` (newest
        first); soft-deleted users are excluded by the default manager.
    """
    safe_page = max(page, MIN_PAGE)
    safe_page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    queryset: QuerySet[User] = User.objects.filter(tenant_id=tenant_id)

    if q is not None:
        trimmed = q.strip()[:MAX_QUERY_LENGTH]
        if trimmed:
            queryset = queryset.filter(email__icontains=trimmed)

    if status is UserStatus.ACTIVE:
        queryset = queryset.filter(is_active=True)
    elif status is UserStatus.INACTIVE:
        queryset = queryset.filter(is_active=False)
    elif status is UserStatus.STAFF:
        queryset = queryset.filter(is_staff=True)

    queryset = queryset.only(
        "id",
        "email",
        "is_active",
        "is_staff",
        "created_at",
        "last_login",
    ).order_by("-created_at", "-id")

    total = queryset.count()
    offset = (safe_page - MIN_PAGE) * safe_page_size
    rows = list(queryset[offset : offset + safe_page_size])

    return rows, total
