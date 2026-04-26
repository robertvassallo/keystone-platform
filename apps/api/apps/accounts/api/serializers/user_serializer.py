"""Serializer — public read shape for a User."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User

from .account_serializer import TenantSummarySerializer


class UserSerializer(serializers.ModelSerializer[User]):
    """Read-only projection used by ``/auth/me/`` and auth response bodies."""

    tenant = TenantSummarySerializer(read_only=True)

    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "is_active",
            "is_staff",
            "tenant",
            "email_verified_at",
            "created_at",
        )
        read_only_fields = fields
