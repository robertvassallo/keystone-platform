"""Tests for the get_mfa_status service."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import MFARecoveryCode
from apps.accounts.services import get_mfa_status
from apps.accounts.services._mfa_helpers import hash_recovery_code
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_status_when_user_has_no_device() -> None:
    user = UserFactory()

    status = get_mfa_status(user=user)

    assert status == {"enabled": False, "recovery_codes_remaining": 0}


@pytest.mark.django_db
def test_status_when_device_unconfirmed_treats_user_as_disabled() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=False)

    status = get_mfa_status(user=user)

    assert status["enabled"] is False


@pytest.mark.django_db
def test_status_when_enrolled_counts_only_unused_recovery_codes() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    MFARecoveryCode.objects.bulk_create(
        [
            MFARecoveryCode(user=user, code_hash=hash_recovery_code("AAAA1111")),
            MFARecoveryCode(user=user, code_hash=hash_recovery_code("BBBB2222")),
            MFARecoveryCode(user=user, code_hash=hash_recovery_code("CCCC3333")),
        ],
    )
    MFARecoveryCode.objects.filter(
        user=user, code_hash=hash_recovery_code("AAAA1111"),
    ).update(consumed_at="2026-04-25T00:00:00Z")

    status = get_mfa_status(user=user)

    assert status == {"enabled": True, "recovery_codes_remaining": 2}
