"""Serializer — request a password-reset email."""

from __future__ import annotations

from rest_framework import serializers

MAX_EMAIL_LENGTH = 254


class PasswordResetRequestSerializer(serializers.Serializer[None]):
    """Just the email — no leak about whether it's registered."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)
