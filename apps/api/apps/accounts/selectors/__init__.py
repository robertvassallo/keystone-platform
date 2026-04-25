"""Public selector surface — read queries, no side effects."""

from .get_user_by_email import get_user_by_email

__all__ = ["get_user_by_email"]
