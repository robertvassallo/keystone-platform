"""Serializer — change-password payload validation."""

from __future__ import annotations

from rest_framework import serializers

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


class ChangePasswordSerializer(serializers.Serializer[None]):
    """Requires the current password to authorize the change."""

    current_password = serializers.CharField(
        write_only=True,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
