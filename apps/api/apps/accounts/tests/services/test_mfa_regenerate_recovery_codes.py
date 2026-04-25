"""Tests for the regenerate_recovery_codes service."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import MFANotEnrolled, WrongCurrentPassword
from apps.accounts.models import MFARecoveryCode
from apps.accounts.services import regenerate_recovery_codes
from apps.accounts.services._mfa_helpers import (
    RECOVERY_CODE_COUNT,
    hash_recovery_code,
)
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory


@pytest.mark.django_db
def test_regenerate_replaces_existing_codes() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    MFARecoveryCode.objects.create(
        user=user, code_hash=hash_recovery_code("OLDCODE1"),
    )

    new_codes = regenerate_recovery_codes(
        user=user, current_password=DEFAULT_TEST_PASSWORD,
    )

    assert len(new_codes) == RECOVERY_CODE_COUNT
    assert MFARecoveryCode.objects.filter(user=user).count() == RECOVERY_CODE_COUNT
    assert not MFARecoveryCode.objects.filter(
        user=user, code_hash=hash_recovery_code("OLDCODE1"),
    ).exists()


@pytest.mark.django_db
def test_regenerate_raises_on_wrong_password() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)

    with pytest.raises(WrongCurrentPassword):
        regenerate_recovery_codes(
            user=user, current_password="not-the-password",
        )


@pytest.mark.django_db
def test_regenerate_raises_when_user_is_not_enrolled() -> None:
    user = UserFactory()

    with pytest.raises(MFANotEnrolled):
        regenerate_recovery_codes(
            user=user, current_password=DEFAULT_TEST_PASSWORD,
        )
