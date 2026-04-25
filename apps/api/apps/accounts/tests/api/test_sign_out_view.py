"""Tests for POST /api/v1/auth/sign-out/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

SIGN_IN_URL = "/api/v1/auth/sign-in/"
SIGN_OUT_URL = "/api/v1/auth/sign-out/"
ME_URL = "/api/v1/auth/me/"


@pytest.mark.django_db
def test_sign_out_clears_session_and_subsequent_me_returns_401() -> None:
    user = UserFactory(email="signout@example.com")
    client = APIClient(enforce_csrf_checks=False)
    client.post(
        SIGN_IN_URL,
        {"email": user.email, "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )
    assert client.get(ME_URL).status_code == 200

    response = client.post(SIGN_OUT_URL)

    assert response.status_code == 204
    assert client.get(ME_URL).status_code == 401


@pytest.mark.django_db
def test_sign_out_when_not_signed_in_returns_204() -> None:
    client = APIClient()

    response = client.post(SIGN_OUT_URL)

    assert response.status_code == 204
