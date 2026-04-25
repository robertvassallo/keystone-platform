"""Account — the tenant entity.

A user belongs to exactly one Account today (the relationship is 1:1).
The "owner" is implicit: the single ``User`` whose ``tenant`` FK points
at this Account. When invite / membership flows ship, an explicit
``owner`` field will land alongside the membership table.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models
from django.utils import timezone

from ._uuid import uuid_v7


class Account(models.Model):
    """A tenant. One Account per signed-up user today."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid_v7,
        editable=False,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=100,
        help_text="Lowercase URL-safe identifier; unique among non-deleted accounts.",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accounts_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accounts_updated",
    )

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accounts_deleted",
    )

    class Meta:
        db_table = "accounts"
        ordering: ClassVar[list[str]] = ["-created_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_accounts_slug_active",
            ),
        ]

    def __str__(self) -> str:
        return self.name
