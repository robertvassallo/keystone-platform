"""Per-request middleware: bind the user's tenant to the DB connection.

Runs after Django's ``AuthenticationMiddleware``. Two subtleties:

1. Accessing ``request.user`` triggers Django's lazy session-user fetch
   on the connection. That fetch queries ``user_accounts``, which is
   RLS-protected — so we wrap the access in ``bypass_rls()`` to guarantee
   it succeeds before we know the tenant.
2. The session vars set by ``set_request_session_vars`` use ``SET``
   (connection-scoped, not transaction-scoped) so they persist across
   the multiple queries the view will issue. They're reset on the next
   request when the middleware runs again.

Posture per request:
* **Anonymous / pre-auth flows** (sign-in, sign-up, password-reset,
  invite-accept, email-verify) → ``bypass_rls = on``. These flows
  legitimately need cross-tenant lookups (find user by email, find
  invite by token) before authentication completes.
* **Authenticated, non-admin** → ``bypass_rls = off``,
  ``current_tenant_id = user.tenant_id``. RLS policies enforce
  per-tenant isolation on ``user_accounts``, ``invites``,
  ``audit_events``.
* **Django admin** (``/admin/``) → ``bypass_rls = on``. Admin staff
  legitimately need cross-tenant access via the Django admin UI.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse

from apps.accounts.models import User
from apps.accounts.security.rls import bypass_rls, set_request_session_vars

ADMIN_PATH_PREFIX = "/admin/"


class RLSMiddleware:
    """Set ``app.current_tenant_id`` and ``app.bypass_rls`` per request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Wire the middleware to its downstream get_response."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Apply the per-request RLS scope, then dispatch."""
        # Resolve the request user under bypass so the auth backend's
        # ``user_accounts`` lookup can't be blocked by stale RLS state.
        with bypass_rls():
            user: Any = getattr(request, "user", None)
            is_authed = isinstance(user, User) and user.is_authenticated
            tenant_id = user.tenant_id if is_authed else None

        is_admin_path = request.path.startswith(ADMIN_PATH_PREFIX)
        # Bypass when:
        #   - serving the Django admin (cross-tenant by design),
        #   - serving an anonymous / pre-auth flow (no tenant context).
        # Otherwise scope strictly to the user's tenant.
        bypass = is_admin_path or not is_authed

        set_request_session_vars(tenant_id=tenant_id, bypass=bypass)
        return self.get_response(request)
