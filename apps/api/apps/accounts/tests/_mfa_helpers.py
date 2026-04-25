"""Shared helpers for MFA tests."""

from __future__ import annotations

from django_otp.oath import totp as _compute_totp
from django_otp.plugins.otp_totp.models import TOTPDevice


def current_totp_code(device: TOTPDevice) -> str:
    """Compute the TOTP code an authenticator app would currently emit."""
    code = _compute_totp(
        device.bin_key,
        step=device.step,
        t0=device.t0,
        digits=device.digits,
    )
    return f"{code:0{device.digits}d}"
