"""Reusable DRF permission classes.

Two layers exist:

* **Platform** (``IsStaff``) — Django's ``is_staff`` flag. Reserved for
  cross-tenant operations and the Django admin. Unused on any API view
  today; kept as the gate for future "Keystone employee" surfaces.
* **Tenant** (``IsTenantOwnerOrStaff``) — the per-tenant admin role.
  ``True`` when the request user is the ``Account.owner`` of their own
  tenant, OR when ``is_staff`` is set (so platform-staff can still
  administer for support).

When ``Membership`` lands, ``IsTenantOwnerOrStaff`` extends to "owner OR
admin role on this tenant"; the public name stays the same.
"""

from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView


class IsStaff(IsAuthenticated):
    """Allow access only to authenticated users with ``is_staff=True``."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Authenticated AND ``is_staff=True``."""
        if not super().has_permission(request, view):
            return False
        return bool(getattr(request.user, "is_staff", False))


class IsTenantOwnerOrStaff(IsAuthenticated):
    """Allow access to the tenant's owner or to platform staff.

    Reads ``user.tenant.owner_id`` — both are populated for any signed-in
    user (``user.tenant`` is non-null per the ``accounts-tenancy`` PR;
    ``Account.owner`` is set during sign-up and backfilled for legacy
    rows). Platform staff bypass the owner check entirely.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Authenticated AND (tenant owner OR ``is_staff=True``)."""
        if not super().has_permission(request, view):
            return False
        user = request.user
        if getattr(user, "is_staff", False):
            return True
        tenant = getattr(user, "tenant", None)
        if tenant is None:
            return False
        return bool(tenant.owner_id == user.id)
