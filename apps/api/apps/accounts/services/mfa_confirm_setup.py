"""Service — verify the first TOTP code and finalize MFA enrolment."""

from __future__ import annotations

from django.db import transaction
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import (
    InvalidMFACode,
    MFAAlreadyEnrolled,
    MFANotEnrolled,
)
from apps.accounts.models import MFARecoveryCode, User

from ._mfa_helpers import generate_recovery_codes, hash_recovery_code


def confirm_mfa_setup(*, user: User, code: str) -> list[str]:
    """Confirm the user's pending TOTP device and return new recovery codes.

    Args:
        user: Authenticated user with a pending (unconfirmed) device.
        code: Six-digit TOTP code from the authenticator app.

    Returns:
        A fresh list of plaintext recovery codes. They're shown once and
        stored hashed; the caller must surface them to the user.

    Raises:
        MFAAlreadyEnrolled: If the user already has a confirmed device.
        MFANotEnrolled: If no unconfirmed device exists (caller forgot to
            run ``start_mfa_setup``).
        InvalidMFACode: If the supplied code does not validate.
    """
    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        raise MFAAlreadyEnrolled(
            "MFA is already enabled for this account.",
        )

    device = (
        TOTPDevice.objects.filter(user=user, confirmed=False)
        .order_by("-id")
        .first()
    )
    if device is None:
        raise MFANotEnrolled(
            "No pending MFA setup found. Start a new setup first.",
        )

    if not device.verify_token(code):
        raise InvalidMFACode("Invalid authentication code.")

    with transaction.atomic():
        device.confirmed = True
        device.save(update_fields=["confirmed"])

        # Any sibling unconfirmed devices are stale — drop them.
        TOTPDevice.objects.filter(
            user=user, confirmed=False,
        ).exclude(pk=device.pk).delete()

        # Replace any stale recovery codes from a prior aborted setup.
        MFARecoveryCode.objects.filter(user=user).delete()

        codes = generate_recovery_codes()
        MFARecoveryCode.objects.bulk_create(
            MFARecoveryCode(user=user, code_hash=hash_recovery_code(code))
            for code in codes
        )

    return codes
