"""Postgres Row-Level Security helpers.

Two session variables drive the RLS policies:

* ``app.current_tenant_id`` — set per authenticated request by
  ``RLSMiddleware``. Policies on tenant-scoped tables compare each row's
  ``tenant_id`` against this value.
* ``app.bypass_rls`` — when set to ``'on'``, policies are satisfied
  unconditionally. Used for legitimate cross-tenant flows
  (sign-in lookup, invite preview, password reset) and for system
  contexts (migrations, management commands, tests).

Both are set with ``SET LOCAL`` so they're scoped to the current
transaction and roll back / reset cleanly. The context managers below
ensure an explicit transaction is open.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from uuid import UUID

from django.db import connection, transaction


@contextmanager
def bypass_rls() -> Any:
    """Run a block with RLS policies satisfied via the bypass flag."""
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.bypass_rls = 'on'")
        try:
            yield
        finally:
            # SET LOCAL is automatically scoped to the transaction; the
            # explicit RESET is belt-and-braces in case the caller is
            # nesting inside a longer-lived transaction.
            cursor.execute("RESET app.bypass_rls")


@contextmanager
def tenant_scope(tenant_id: UUID) -> Any:
    """Run a block under a specific tenant's RLS scope (clears bypass)."""
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            "SET LOCAL app.current_tenant_id = %s",
            [str(tenant_id)],
        )
        cursor.execute("SET LOCAL app.bypass_rls = 'off'")
        try:
            yield
        finally:
            cursor.execute("RESET app.current_tenant_id")
            cursor.execute("RESET app.bypass_rls")


def set_request_session_vars(*, tenant_id: UUID | None, bypass: bool) -> None:
    """Apply the RLS session vars for the current request's connection.

    Used by ``RLSMiddleware``; called inside the request's already-active
    transaction (Django opens one when ``ATOMIC_REQUESTS`` is on, or the
    middleware opens a short one). ``SET`` (not ``SET LOCAL``) so the
    setting persists across the multiple statements the view will issue.
    """
    with connection.cursor() as cursor:
        if tenant_id is not None:
            cursor.execute(
                "SET app.current_tenant_id = %s",
                [str(tenant_id)],
            )
        else:
            cursor.execute("RESET app.current_tenant_id")
        cursor.execute(
            "SET app.bypass_rls = %s",
            ["on" if bypass else "off"],
        )
