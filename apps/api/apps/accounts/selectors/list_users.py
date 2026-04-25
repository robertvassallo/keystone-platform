"""Selector — paginated read-only list of users."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import User

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
MIN_PAGE = 1


def list_users(
    *,
    page: int = MIN_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> tuple[list[User], int]:
    """Return (rows, total_count) for the given page.

    Args:
        page: 1-indexed page. Values < 1 are clamped to 1.
        page_size: Rows per page. Clamped to [1, MAX_PAGE_SIZE].

    Returns:
        Tuple of the page's rows and the unfiltered total count.
        Sort is fixed to ``-created_at`` (newest first); soft-deleted
        users are excluded by the default manager.
    """
    safe_page = max(page, MIN_PAGE)
    safe_page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    queryset: QuerySet[User] = User.objects.only(
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
