"""Manager for the User model.

The default manager hides soft-deleted rows; ``all_with_deleted`` exposes
the raw queryset for admin / restoration paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager
from django.db.models import QuerySet

if TYPE_CHECKING:
    from apps.accounts.models import User


class UserManager(BaseUserManager["User"]):
    """Custom manager — email is the natural key, soft-delete aware."""

    use_in_migrations = True

    def get_queryset(self) -> QuerySet[User]:
        """Default queryset hides soft-deleted rows."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self) -> QuerySet[User]:
        """Escape hatch — includes soft-deleted rows."""
        return super().get_queryset()

    def _create(self, email: str, password: str | None, **extra_fields: Any) -> User:
        if not email:
            raise ValueError("Email is required.")
        normalized_email = self.normalize_email(email).lower()
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a regular user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a superuser (full admin)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create(email, password, **extra_fields)
