"""Service — initiate MFA enrolment by creating an unconfirmed TOTPDevice."""

from __future__ import annotations

from typing import TypedDict

from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import MFAAlreadyEnrolled
from apps.accounts.models import User

from ._mfa_helpers import make_qr_data_url, secret_from_device


class MFASetupPayload(TypedDict):
    """Payload returned by ``start_mfa_setup``."""

    secret: str
    provisioning_uri: str
    qr_data_url: str


def start_mfa_setup(*, user: User) -> MFASetupPayload:
    """Create (or replace) the user's unconfirmed TOTP device.

    Returns the bits the frontend needs to render the enrolment QR + the
    manual-entry fallback. The device stays unconfirmed until
    ``confirm_mfa_setup`` validates a code from the authenticator app.

    Raises:
        MFAAlreadyEnrolled: If the user already has a confirmed device.
    """
    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        raise MFAAlreadyEnrolled(
            "MFA is already enabled for this account.",
        )

    # Drop any prior half-finished setups so a fresh start is unambiguous.
    TOTPDevice.objects.filter(user=user, confirmed=False).delete()

    device = TOTPDevice.objects.create(
        user=user,
        name="default",
        confirmed=False,
    )

    return {
        "secret": secret_from_device(device.bin_key),
        "provisioning_uri": device.config_url,
        "qr_data_url": make_qr_data_url(device.config_url),
    }
