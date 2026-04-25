"""Tests for the start_mfa_setup service."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import MFAAlreadyEnrolled
from apps.accounts.services import start_mfa_setup
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_start_setup_returns_secret_uri_and_qr_for_first_time_user() -> None:
    user = UserFactory()

    payload = start_mfa_setup(user=user)

    assert payload["secret"]
    assert payload["provisioning_uri"].startswith("otpauth://totp/")
    assert payload["qr_data_url"].startswith("data:image/png;base64,")
    assert TOTPDevice.objects.filter(user=user, confirmed=False).count() == 1


@pytest.mark.django_db
def test_start_setup_replaces_stale_unconfirmed_device() -> None:
    user = UserFactory()
    first = TOTPDevice.objects.create(user=user, name="default", confirmed=False)

    start_mfa_setup(user=user)

    assert not TOTPDevice.objects.filter(pk=first.pk).exists()
    assert TOTPDevice.objects.filter(user=user, confirmed=False).count() == 1


@pytest.mark.django_db
def test_start_setup_raises_when_user_already_enrolled() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)

    with pytest.raises(MFAAlreadyEnrolled):
        start_mfa_setup(user=user)
