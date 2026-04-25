"""Tests for POST /api/v1/auth/mfa/verify/."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from freezegun import freeze_time
from rest_framework.test import APIClient

from apps.accounts.models import MFARecoveryCode, User
from apps.accounts.services._mfa_helpers import hash_recovery_code
from apps.accounts.tests._mfa_helpers import current_totp_code
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

SIGN_IN_URL = "/api/v1/auth/sign-in/"
VERIFY_URL = "/api/v1/auth/mfa/verify/"
ME_URL = "/api/v1/auth/me/"


def _sign_in_to_challenge(client: APIClient, user: User) -> None:
    """Hit sign-in to provoke the 202 challenge response — sets the session ticket."""
    response = client.post(
        SIGN_IN_URL,
        {"email": user.email, "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )
    assert response.status_code == 202


@pytest.mark.django_db
def test_verify_with_valid_totp_returns_200_and_signs_user_in() -> None:
    user = UserFactory()
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    _sign_in_to_challenge(client, user)

    response = client.post(
        VERIFY_URL,
        {"code": current_totp_code(device)},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert client.get(ME_URL).status_code == 200


@pytest.mark.django_db
def test_verify_with_recovery_code_consumes_it() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    plaintext = "AAAA1111"
    MFARecoveryCode.objects.create(
        user=user, code_hash=hash_recovery_code(plaintext),
    )
    client = APIClient()
    _sign_in_to_challenge(client, user)

    first = client.post(VERIFY_URL, {"code": plaintext}, format="json")

    assert first.status_code == 200
    consumed = MFARecoveryCode.objects.get(user=user)
    assert consumed.consumed_at is not None

    # Re-using the same recovery code should fail (a fresh challenge is
    # needed; new sign-in re-stashes a ticket).
    client.post(
        SIGN_IN_URL,
        {"email": user.email, "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )
    second = client.post(VERIFY_URL, {"code": plaintext}, format="json")
    assert second.status_code == 422
    assert second.json()["type"].endswith("invalid_mfa_code")


@pytest.mark.django_db
def test_verify_with_wrong_code_returns_422_and_keeps_ticket_for_retry() -> None:
    user = UserFactory()
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()
    _sign_in_to_challenge(client, user)

    wrong = client.post(VERIFY_URL, {"code": "000000"}, format="json")
    assert wrong.status_code == 422
    assert wrong.json()["type"].endswith("invalid_mfa_code")

    correct = client.post(
        VERIFY_URL, {"code": current_totp_code(device)}, format="json",
    )
    assert correct.status_code == 200


@pytest.mark.django_db
def test_verify_without_a_session_ticket_returns_422_expired() -> None:
    client = APIClient()

    response = client.post(VERIFY_URL, {"code": "123456"}, format="json")

    assert response.status_code == 422
    assert response.json()["type"].endswith("mfa_challenge_expired")


@pytest.mark.django_db
def test_verify_with_expired_ticket_returns_422_expired() -> None:
    user = UserFactory()
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()

    with freeze_time(timezone.now()) as frozen:
        _sign_in_to_challenge(client, user)
        frozen.tick(delta=timedelta(minutes=6))
        response = client.post(
            VERIFY_URL, {"code": current_totp_code(device)}, format="json",
        )

    assert response.status_code == 422
    assert response.json()["type"].endswith("mfa_challenge_expired")
