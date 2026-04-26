"""Action codes for the audit log.

Namespaced by domain (``auth``, ``mfa``, ``invite``, ``tenant``). Codes are
stable identifiers — never rename one in place; deprecate and add a new
code instead, since stored ``AuditEvent.action`` values reference them.
"""

from __future__ import annotations

from enum import StrEnum


class AuditAction(StrEnum):
    """Mutually-exclusive set of action codes recorded in the audit log."""

    # Authentication
    AUTH_SIGN_IN = "auth.sign_in"
    AUTH_PASSWORD_CHANGE = "auth.password_change"  # noqa: S105 — action code, not a credential

    # Multi-factor
    MFA_ENROLLED = "mfa.enrolled"
    MFA_DISABLED = "mfa.disabled"
    MFA_RECOVERY_CODES_REGENERATED = "mfa.recovery_codes_regenerated"

    # Invites
    INVITE_SENT = "invite.sent"
    INVITE_REVOKED = "invite.revoked"
    INVITE_ACCEPTED = "invite.accepted"

    # Tenant
    TENANT_RENAMED = "tenant.renamed"
