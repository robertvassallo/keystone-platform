"""Serializer — sign-in payload validation."""

from __future__ import annotations

from rest_framework import serializers

MAX_PASSWORD_LENGTH = 128
MAX_EMAIL_LENGTH = 254


class SignInSerializer(serializers.Serializer[None]):
    """Email + password + remember-me flag for sign-in."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)
    password = serializers.CharField(
        write_only=True,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )
    remember_me = serializers.BooleanField(default=False)
