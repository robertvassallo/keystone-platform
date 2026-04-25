"""Public selector surface — read queries, no side effects."""

from .get_user_by_email import get_user_by_email
from .list_users import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MIN_PAGE,
    list_users,
)

__all__ = [
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MIN_PAGE",
    "get_user_by_email",
    "list_users",
]
