"""Invite — token-bearing invitation for a new user to join a tenant.

Plaintext tokens never live in the database; only their SHA-256 hex
digest does. The plaintext is generated server-side via
``secrets.token_urlsafe`` and embedded in the URL of the invite email
exactly once. Single-use and time-bounded — see ``services/_invite_token.py``.

Lifecycle:
- Created by a staff user; ``accepted_at`` and ``revoked_at`` start null.
- Accepting sets ``accepted_at`` + ``accepted_by``. The created User's
  ``tenant`` FK points at this Invite's ``tenant``.
- Revoking sets ``revoked_at``.
- Pending = ``accepted_at IS NULL AND revoked_at IS NULL AND expires_at > now``.

Partial unique index: at most one *pending* invite per ``(tenant, email)``
pair. Re-inviting after revoke or after acceptance both work.
"""

from __future__ import annotations

import datetime as dt
from typing import ClassVar

from django.conf import settings
from django.db import models
from django.utils import timezone

from ._uuid import uuid_v7

INVITE_TTL = dt.timedelta(days=7)


def _default_expires_at() -> dt.datetime:
    return timezone.now() + INVITE_TTL


class Invite(models.Model):
    """A pending or completed invitation to join a tenant."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid_v7,
        editable=False,
    )
    tenant = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="invites",
        db_column="tenant_id",
    )
    email = models.EmailField(
        max_length=254,
        help_text="Lowercased invitee address. Not unique across the table.",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invites_sent",
    )
    token_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hex digest of the plaintext token. Plaintext is "
        "never stored.",
    )
    expires_at = models.DateTimeField(default=_default_expires_at)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="invite_accepted",
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invites_revoked",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invites"
        ordering: ClassVar[list[str]] = ["-created_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["tenant", "email"],
                condition=models.Q(
                    accepted_at__isnull=True,
                    revoked_at__isnull=True,
                ),
                name="uq_invites_pending_tenant_email",
            ),
        ]

    def __str__(self) -> str:
        return f"Invite(tenant={self.tenant_id}, email={self.email})"

    @property
    def is_pending(self) -> bool:
        """True iff the invite is still consumable."""
        return (
            self.accepted_at is None
            and self.revoked_at is None
            and self.expires_at > timezone.now()
        )
