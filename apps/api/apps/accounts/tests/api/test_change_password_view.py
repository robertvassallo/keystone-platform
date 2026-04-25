"""Tests for POST /api/v1/auth/password/change/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

URL = "/api/v1/auth/password/change/"
NEW_PASSWORD = "Even-Stronger-Password-2026"


@pytest.mark.django_db
def test_returns_204_and_session_persists_after_successful_change() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        URL,
        {
            "current_password": DEFAULT_TEST_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
        format="json",
    )
    user.refresh_from_db()

    assert response.status_code == 204
    assert user.check_password(NEW_PASSWORD)
    assert client.get("/api/v1/auth/me/").status_code == 200


@pytest.mark.django_db
def test_returns_401_when_anonymous() -> None:
    client = APIClient()

    response = client.post(
        URL,
        {"current_password": "anything", "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_returns_422_on_wrong_current_password() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        URL,
        {"current_password": "wrong-password-1234", "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["type"].endswith("wrong_current_password")


@pytest.mark.django_db
def test_returns_400_on_weak_new_password() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        URL,
        {
            "current_password": DEFAULT_TEST_PASSWORD,
            "new_password": "short",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "new_password" in response.json().get("errors", {})
