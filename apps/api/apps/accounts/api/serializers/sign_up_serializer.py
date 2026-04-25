"""Serializer — sign-up payload validation."""

from __future__ import annotations

from rest_framework import serializers

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 254


class SignUpSerializer(serializers.Serializer[None]):
    """Email + password to create a new user.

    The password is gated by ``AUTH_PASSWORD_VALIDATORS`` inside the
    ``sign_up`` service; this serializer only enforces the cheap
    boundaries (length + email format).
    """

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)
    password = serializers.CharField(
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
