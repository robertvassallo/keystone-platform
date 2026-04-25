"""End-to-end tests for the /api/v1/auth/mfa/ endpoints."""

from __future__ import annotations

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient

from apps.accounts.models import MFARecoveryCode
from apps.accounts.services._mfa_helpers import RECOVERY_CODE_COUNT
from apps.accounts.tests._mfa_helpers import current_totp_code
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

STATUS_URL = "/api/v1/auth/mfa/status/"
SETUP_URL = "/api/v1/auth/mfa/setup/"
SETUP_CONFIRM_URL = "/api/v1/auth/mfa/setup/confirm/"
DISABLE_URL = "/api/v1/auth/mfa/disable/"
REGENERATE_URL = "/api/v1/auth/mfa/recovery-codes/regenerate/"


@pytest.mark.django_db
def test_status_returns_disabled_for_new_user() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.get(STATUS_URL)

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "recovery_codes_remaining": 0,
    }


@pytest.mark.django_db
def test_status_returns_401_when_anonymous() -> None:
    response = APIClient().get(STATUS_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_full_enrol_flow_sets_status_enabled_with_ten_codes() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    setup = client.post(SETUP_URL).json()
    device = TOTPDevice.objects.get(user=user, confirmed=False)

    confirm = client.post(
        SETUP_CONFIRM_URL,
        {"code": current_totp_code(device)},
        format="json",
    )
    status_after = client.get(STATUS_URL).json()

    assert "secret" in setup
    assert setup["provisioning_uri"].startswith("otpauth://")
    assert confirm.status_code == 200
    assert len(confirm.json()["recovery_codes"]) == RECOVERY_CODE_COUNT
    assert status_after == {
        "enabled": True,
        "recovery_codes_remaining": RECOVERY_CODE_COUNT,
    }


@pytest.mark.django_db
def test_setup_confirm_returns_422_on_wrong_code() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)
    client.post(SETUP_URL)

    response = client.post(
        SETUP_CONFIRM_URL, {"code": "000000"}, format="json",
    )

    assert response.status_code == 422
    assert response.json()["type"].endswith("invalid_mfa_code")


@pytest.mark.django_db
def test_setup_returns_422_when_already_enrolled() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    client.force_login(user)

    response = client.post(SETUP_URL)

    assert response.status_code == 422
    assert response.json()["type"].endswith("mfa_already_enrolled")


@pytest.mark.django_db
def test_disable_clears_state_with_correct_password() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    client.force_login(user)

    response = client.post(
        DISABLE_URL,
        {"current_password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 204
    assert not TOTPDevice.objects.filter(user=user).exists()
    assert not MFARecoveryCode.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_disable_returns_422_on_wrong_password() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    client.force_login(user)

    response = client.post(
        DISABLE_URL,
        {"current_password": "wrong-password-1234"},
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["type"].endswith("wrong_current_password")


@pytest.mark.django_db
def test_regenerate_replaces_codes_with_correct_password() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    client.force_login(user)

    response = client.post(
        REGENERATE_URL,
        {"current_password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.json()["recovery_codes"]) == RECOVERY_CODE_COUNT
    assert MFARecoveryCode.objects.filter(user=user).count() == RECOVERY_CODE_COUNT


@pytest.mark.django_db
def test_regenerate_returns_422_when_not_enrolled() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        REGENERATE_URL,
        {"current_password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["type"].endswith("mfa_not_enrolled")
