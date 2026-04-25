"""Tests for POST /api/v1/auth/sign-in/."""

from __future__ import annotations

import pytest
from django.conf import settings
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient

from apps.accounts.services.mfa_verify_challenge import CHALLENGE_SESSION_KEY
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

URL = "/api/v1/auth/sign-in/"


@pytest.mark.django_db
def test_sign_in_returns_200_and_user_on_correct_credentials() -> None:
    user = UserFactory(email="signin@example.com")
    client = APIClient()

    response = client.post(
        URL,
        {"email": user.email, "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "signin@example.com"


@pytest.mark.django_db
def test_sign_in_returns_401_problem_details_on_wrong_password() -> None:
    UserFactory(email="user@example.com")
    client = APIClient()

    response = client.post(
        URL,
        {"email": "user@example.com", "password": "wrong-password-1234"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["type"].endswith("invalid_credentials")


@pytest.mark.django_db
def test_sign_in_returns_401_for_unknown_email_without_leaking_existence() -> None:
    client = APIClient()

    response = client.post(
        URL,
        {"email": "ghost@example.com", "password": "any-password-123-XY"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["type"].endswith("invalid_credentials")


@pytest.mark.django_db
def test_sign_in_returns_202_when_user_has_mfa_enrolled() -> None:
    user = UserFactory(email="mfa@example.com")
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    client = APIClient()

    response = client.post(
        URL,
        {"email": user.email, "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 202
    assert response.json() == {"mfa_required": True}
    # The session was issued so the verify endpoint can find the partial ticket.
    assert client.session.get(CHALLENGE_SESSION_KEY) is not None


@pytest.mark.django_db
def test_sign_in_with_remember_me_sets_30_day_session() -> None:
    user = UserFactory(email="remember@example.com")
    client = APIClient()

    response = client.post(
        URL,
        {
            "email": user.email,
            "password": DEFAULT_TEST_PASSWORD,
            "remember_me": True,
        },
        format="json",
    )

    assert response.status_code == 200
    session_cookie = response.cookies.get("sessionid")
    assert session_cookie is not None
    # max-age in cookie reflects REMEMBER_ME_DURATION
    assert int(session_cookie["max-age"]) == settings.REMEMBER_ME_DURATION
