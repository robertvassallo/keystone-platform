"""Tests for GET /api/v1/auth/me/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/me/"


@pytest.mark.django_db
def test_me_returns_200_with_serialized_user_when_authenticated() -> None:
    user = UserFactory(email="me@example.com")
    client = APIClient()
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"
    assert "id" in body


@pytest.mark.django_db
def test_me_returns_401_when_anonymous() -> None:
    client = APIClient()

    response = client.get(URL)

    assert response.status_code == 401
    assert response.json()["status"] == 401
