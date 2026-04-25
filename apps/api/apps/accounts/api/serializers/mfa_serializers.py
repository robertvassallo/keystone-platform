"""Serializers for the MFA endpoints — request and response shapes."""

from __future__ import annotations

from rest_framework import serializers

TOTP_CODE_LENGTH = 6
RECOVERY_CODE_MAX_LENGTH = 16
MAX_PASSWORD_LENGTH = 128


class MFASetupConfirmSerializer(serializers.Serializer[None]):
    """Six-digit code from the authenticator app."""

    code = serializers.RegexField(
        regex=r"^\d{6}$",
        max_length=TOTP_CODE_LENGTH,
    )


class MFAPasswordConfirmSerializer(serializers.Serializer[None]):
    """Re-prompt for the current password before disable / regenerate."""

    current_password = serializers.CharField(
        write_only=True,
        max_length=MAX_PASSWORD_LENGTH,
        trim_whitespace=False,
    )


class MFAStatusResponseSerializer(serializers.Serializer[None]):
    """Read shape returned by ``GET /mfa/status/``."""

    enabled = serializers.BooleanField(read_only=True)
    recovery_codes_remaining = serializers.IntegerField(read_only=True)


class MFASetupResponseSerializer(serializers.Serializer[None]):
    """Read shape returned by ``POST /mfa/setup/``."""

    secret = serializers.CharField(read_only=True)
    provisioning_uri = serializers.CharField(read_only=True)
    qr_data_url = serializers.CharField(read_only=True)


class MFARecoveryCodesResponseSerializer(serializers.Serializer[None]):
    """Read shape returned by setup-confirm and regenerate endpoints."""

    recovery_codes = serializers.ListField(
        child=serializers.CharField(max_length=RECOVERY_CODE_MAX_LENGTH),
        read_only=True,
    )
