"""Serializers for the invites API."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import Invite

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 254


class InviteCreateSerializer(serializers.Serializer[None]):
    """Body for ``POST /api/v1/invites/``."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)


class InviteSerializer(serializers.ModelSerializer[Invite]):
    """Read shape for invite list / send-response. No token leakage."""

    invited_by_email = serializers.CharField(
        source="invited_by.email",
        read_only=True,
    )
    status = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = (
            "id",
            "email",
            "invited_by_email",
            "status",
            "expires_at",
            "accepted_at",
            "revoked_at",
            "created_at",
        )
        read_only_fields = fields

    def get_status(self, obj: Invite) -> str:
        """Compute the public-visible state from the row's columns."""
        if obj.accepted_at is not None:
            return "accepted"
        if obj.revoked_at is not None:
            return "revoked"
        if not obj.is_pending:
            return "expired"
        return "pending"


class InvitePreviewSerializer(serializers.Serializer[None]):
    """Read shape for the public preview endpoint — minimal metadata."""

    tenant_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)


class InviteAcceptSerializer(serializers.Serializer[None]):
    """Body for ``POST /api/v1/auth/invite/accept/``."""

    uid = serializers.CharField(max_length=64)
    token = serializers.CharField(max_length=128)
    password = serializers.CharField(
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
