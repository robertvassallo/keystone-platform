"""AuditEvent — immutable, tenant-scoped record of a sensitive action.

Audit events are write-only from the service layer (``services.record_audit_event``).
Rows are never updated or deleted via the application; they're history. Reading is
done via the ``list_audit_events`` selector and the staff-/owner-only audit API.

Snapshotting: ``actor_email`` and ``target_label`` are captured at write time so
the list still reads correctly even after the actor or target is soft-deleted.
``actor`` FK is ``SET_NULL`` for the same reason.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models
from django.utils import timezone

from ._uuid import uuid_v7

MAX_ACTION_LENGTH = 64
MAX_TARGET_TYPE_LENGTH = 32
MAX_LABEL_LENGTH = 254
MAX_USER_AGENT_LENGTH = 500


class AuditEvent(models.Model):
    """One row per sensitive action. Append-only."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid_v7,
        editable=False,
    )

    tenant = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="audit_events",
        db_column="tenant_id",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events_as_actor",
        help_text="Null for system actions or after the actor is removed.",
    )
    actor_email = models.CharField(
        max_length=MAX_LABEL_LENGTH,
        blank=True,
        default="",
        help_text="Snapshot of the actor's email at write time.",
    )

    action = models.CharField(
        max_length=MAX_ACTION_LENGTH,
        db_index=True,
        help_text="Namespaced action code, e.g. 'auth.sign_in'.",
    )

    target_id = models.UUIDField(null=True, blank=True)
    target_type = models.CharField(
        max_length=MAX_TARGET_TYPE_LENGTH,
        blank=True,
        default="",
    )
    target_label = models.CharField(
        max_length=MAX_LABEL_LENGTH,
        blank=True,
        default="",
        help_text="Short human label captured at write time (e.g. invitee email).",
    )

    metadata = models.JSONField(default=dict, blank=True)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(
        max_length=MAX_USER_AGENT_LENGTH,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        db_index=True,
    )

    class Meta:
        db_table = "audit_events"
        ordering: ClassVar[list[str]] = ["-created_at", "-id"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["tenant", "-created_at"],
                name="ix_audit_tenant_recent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor_email or 'system'}"
