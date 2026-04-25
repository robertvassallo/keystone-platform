"""Serializer — full read shape for a single user (detail view)."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User


class UserDetailSerializer(serializers.ModelSerializer[User]):
    """Full read shape for a single user.

    Richer than ``UserListItemSerializer`` — includes ``is_superuser``
    and ``updated_at`` since the detail surface isn't column-constrained.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "tenant_id",
            "created_at",
            "updated_at",
            "last_login",
        )
        read_only_fields = fields
