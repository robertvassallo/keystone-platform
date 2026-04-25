"""Reusable DRF permission classes."""

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
