"""Serializer — MFA verify payload."""

from __future__ import annotations

from rest_framework import serializers

# Loose upper bound; TOTP is 6 digits and recovery codes are 8 chars,
# but accepting up to 16 leaves room for human typos with separators.
MAX_CODE_LENGTH = 16


class MFAVerifySerializer(serializers.Serializer[None]):
    """Single ``code`` field — TOTP or recovery; the service auto-detects."""

    code = serializers.CharField(
        min_length=6,
        max_length=MAX_CODE_LENGTH,
        trim_whitespace=True,
    )
