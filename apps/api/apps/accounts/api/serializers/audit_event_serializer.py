"""Serializer — read shape for an audit event."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer[AuditEvent]):
    """Public read projection for ``/api/v1/audit/`` rows."""

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "action",
            "actor_email",
            "target_type",
            "target_label",
            "ip",
            "created_at",
        )
        read_only_fields = fields
