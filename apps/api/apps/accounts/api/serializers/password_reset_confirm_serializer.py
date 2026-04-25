"""Serializer — confirm a password reset using uid + token + new password."""

from __future__ import annotations

from rest_framework import serializers

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


class PasswordResetConfirmSerializer(serializers.Serializer[None]):
    """uidb64 and token come from the email link query string."""

    uid = serializers.CharField(max_length=64)
    token = serializers.CharField(max_length=128)
    password = serializers.CharField(
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
