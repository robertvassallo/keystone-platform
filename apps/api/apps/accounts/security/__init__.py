"""Database-side security primitives — RLS context managers."""

from .rls import bypass_rls, tenant_scope

__all__ = ["bypass_rls", "tenant_scope"]
