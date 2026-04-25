"""Tests for the confirm_mfa_setup service."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import (
    InvalidMFACode,
    MFAAlreadyEnrolled,
    MFANotEnrolled,
)
from apps.accounts.models import MFARecoveryCode
from apps.accounts.services import confirm_mfa_setup, start_mfa_setup
from apps.accounts.services._mfa_helpers import (
    RECOVERY_CODE_COUNT,
    RECOVERY_CODE_LENGTH,
    hash_recovery_code,
)
from apps.accounts.tests._mfa_helpers import current_totp_code
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_confirm_setup_marks_device_confirmed_and_returns_recovery_codes() -> None:
    user = UserFactory()
    start_mfa_setup(user=user)
    device = TOTPDevice.objects.get(user=user, confirmed=False)
    code = current_totp_code(device)

    codes = confirm_mfa_setup(user=user, code=code)

    device.refresh_from_db()
    assert device.confirmed is True
    assert len(codes) == RECOVERY_CODE_COUNT
    assert all(len(c) == RECOVERY_CODE_LENGTH for c in codes)
    # Codes are stored hashed.
    for plaintext in codes:
        assert MFARecoveryCode.objects.filter(
            user=user, code_hash=hash_recovery_code(plaintext),
        ).exists()


@pytest.mark.django_db
def test_confirm_setup_raises_invalid_code_for_wrong_value() -> None:
    user = UserFactory()
    start_mfa_setup(user=user)

    with pytest.raises(InvalidMFACode):
        confirm_mfa_setup(user=user, code="000000")

    assert not TOTPDevice.objects.filter(user=user, confirmed=True).exists()
    assert not MFARecoveryCode.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_confirm_setup_raises_when_no_pending_setup() -> None:
    user = UserFactory()

    with pytest.raises(MFANotEnrolled):
        confirm_mfa_setup(user=user, code="123456")


@pytest.mark.django_db
def test_confirm_setup_raises_when_user_already_enrolled() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)

    with pytest.raises(MFAAlreadyEnrolled):
        confirm_mfa_setup(user=user, code="123456")
