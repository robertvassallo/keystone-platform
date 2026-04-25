"""Serializer — public read shape for a User."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    """Read-only projection used by ``/auth/me/`` and auth response bodies."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "tenant_id",
            "created_at",
        )
        read_only_fields = fields
