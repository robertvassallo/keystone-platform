"""Custom User model.

Identified by email (the ``USERNAME_FIELD``); UUID v7 primary key for
time-ordered, non-enumerable identifiers; carries audit + soft-delete
columns per ``docs/01_architecture/data-model.md``. ``tenant_id`` is
nullable today — it becomes required once the tenant scaffolding lands.
"""

from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.accounts.managers import UserManager

from ._uuid import uuid_v7


class User(AbstractBaseUser, PermissionsMixin):
    """Authenticated principal — one row per human."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid_v7,
        editable=False,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        help_text="Lowercased, unique. The login identifier.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="False blocks authentication; soft-delete also flips this.",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Grants access to the Django admin.",
    )

    tenant = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="users",
        db_column="tenant_id",
        help_text="The tenant this user belongs to. Required.",
    )

    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp the user clicked the verification link. Null = unverified.",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_created",
    )
    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_updated",
    )

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_deleted",
    )

    objects: ClassVar[UserManager] = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        db_table = "user_accounts"
        ordering: ClassVar[list[str]] = ["-created_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_user_accounts_email_active",
            ),
        ]

    def __str__(self) -> str:
        return self.email

    def soft_delete(self, *, deleted_by: User | None = None) -> None:
        """Mark the user soft-deleted; deactivate to block auth."""
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.is_active = False
        self.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "is_active",
                "updated_at",
            ],
        )
