"""Per-user MFA recovery codes.

Codes are stored as SHA-256 digests (per ``docs/01_architecture/auth.md``),
never plaintext — the user sees the plaintext exactly once at generation
time. ``consumed_at`` is set when a code is used to complete an MFA
challenge; consumed codes can no longer satisfy a verify.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models
from django.utils import timezone

from ._uuid import uuid_v7


class MFARecoveryCode(models.Model):
    """One single-use recovery code, hashed at rest."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid_v7,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_recovery_codes",
    )
    code_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hex digest of the plaintext code.",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    consumed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "mfa_recovery_codes"
        ordering: ClassVar[list[str]] = ["-created_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["user", "code_hash"],
                name="uq_mfa_recovery_codes_user_code_hash",
            ),
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["user", "consumed_at"],
                name="ix_mfa_rc_user_consumed_at",
            ),
        ]

    def __str__(self) -> str:
        return f"MFARecoveryCode(user={self.user_id}, consumed={self.consumed_at is not None})"
