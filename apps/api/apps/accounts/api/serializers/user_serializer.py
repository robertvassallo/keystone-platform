"""Serializer — public read shape for a User."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User

from .account_serializer import TenantSummarySerializer


class UserSerializer(serializers.ModelSerializer[User]):
    """Read-only projection used by ``/auth/me/`` and auth response bodies."""

    tenant = TenantSummarySerializer(read_only=True)

    display_name = serializers.CharField(read_only=True)
    is_tenant_owner = serializers.SerializerMethodField()

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
            "is_tenant_owner",
            "tenant",
            "email_verified_at",
            "created_at",
        )
        read_only_fields = fields

    def get_is_tenant_owner(self, obj: User) -> bool:
        """True iff the user is the explicit owner of their own tenant."""
        tenant = obj.tenant
        if tenant is None:
            return False
        return obj.id == tenant.owner_id
