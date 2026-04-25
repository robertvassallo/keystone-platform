"""Serializer — full read shape for a single user (detail view)."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User

from .account_serializer import TenantSummarySerializer


class UserDetailSerializer(serializers.ModelSerializer[User]):
    """Full read shape for a single user.

    Richer than ``UserListItemSerializer`` — includes ``is_superuser``,
    ``updated_at``, and a nested tenant summary since the detail surface
    isn't column-constrained.
    """

    tenant = TenantSummarySerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "tenant",
            "created_at",
            "updated_at",
            "last_login",
        )
        read_only_fields = fields
