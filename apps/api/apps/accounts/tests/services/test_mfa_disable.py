"""Tests for the disable_mfa service."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import WrongCurrentPassword
from apps.accounts.models import MFARecoveryCode
from apps.accounts.services import disable_mfa
from apps.accounts.services._mfa_helpers import hash_recovery_code
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory


@pytest.mark.django_db
def test_disable_removes_all_devices_and_recovery_codes() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    MFARecoveryCode.objects.create(
        user=user, code_hash=hash_recovery_code("AAAA1111"),
    )

    disable_mfa(user=user, current_password=DEFAULT_TEST_PASSWORD)

    assert not TOTPDevice.objects.filter(user=user).exists()
    assert not MFARecoveryCode.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_disable_raises_on_wrong_password_and_keeps_state() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)

    with pytest.raises(WrongCurrentPassword):
        disable_mfa(user=user, current_password="not-the-password")

    assert TOTPDevice.objects.filter(user=user, confirmed=True).exists()
