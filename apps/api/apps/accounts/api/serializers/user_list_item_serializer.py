"""Serializer — read shape for a single row of the users list."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User


class UserListItemSerializer(serializers.ModelSerializer[User]):
    """Subset of the User model used by ``GET /api/v1/users/``.

    ``tenant_id`` is intentionally omitted — it is currently nullable and
    will be added once the ``Account`` model lands.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "created_at",
            "last_login",
        )
        read_only_fields = fields
