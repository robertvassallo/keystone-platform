"""Serializers for the Account (tenant) entity."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import Account


class TenantSummarySerializer(serializers.ModelSerializer[Account]):
    """Minimal tenant projection — used inline on User payloads."""

    class Meta:
        model = Account
        fields = ("id", "name", "slug")
        read_only_fields = fields


class AccountSerializer(serializers.ModelSerializer[Account]):
    """Full read shape for the signed-in user's tenant.

    ``owner_email`` is computed — with one user per Account today, it's
    just the (only) member's email. When membership lands the field
    becomes the explicit owner FK.
    """

    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("id", "name", "slug", "owner_email", "created_at")
        read_only_fields = fields

    def get_owner_email(self, obj: Account) -> str | None:
        """Return the email of the (single) member of this Account, or None."""
        first_user = obj.users.order_by("created_at").first()
        return first_user.email if first_user is not None else None
