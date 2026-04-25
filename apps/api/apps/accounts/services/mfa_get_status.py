"""Selector — read-only MFA status for the signed-in user."""

from __future__ import annotations

from typing import TypedDict

from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import MFARecoveryCode, User


class MFAStatus(TypedDict):
    """Shape returned by ``get_mfa_status``."""

    enabled: bool
    recovery_codes_remaining: int


def get_mfa_status(*, user: User) -> MFAStatus:
    """Return whether MFA is enabled and how many recovery codes remain."""
    enabled = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
    remaining = (
        MFARecoveryCode.objects.filter(user=user, consumed_at__isnull=True).count()
        if enabled
        else 0
    )
    return {"enabled": enabled, "recovery_codes_remaining": remaining}
