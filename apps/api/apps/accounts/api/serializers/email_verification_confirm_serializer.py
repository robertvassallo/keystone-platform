"""Serializer — confirm an email-verification token."""

from __future__ import annotations

from rest_framework import serializers


class EmailVerificationConfirmSerializer(serializers.Serializer[None]):
    """uidb64 and token come from the email link query string."""

    uid = serializers.CharField(max_length=64)
    token = serializers.CharField(max_length=128)
