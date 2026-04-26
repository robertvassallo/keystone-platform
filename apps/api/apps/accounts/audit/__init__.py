"""Audit-log domain primitives — action codes, context dataclass."""

from .constants import AuditAction
from .context import AuditContext

__all__ = ["AuditAction", "AuditContext"]
