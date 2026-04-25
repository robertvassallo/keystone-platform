"""Tests for POST /api/v1/auth/password-reset/confirm/."""

from __future__ import annotations

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/password-reset/confirm/"
NEW_PASSWORD = "Brand-New-Password-2026"


def _token_for(user: User) -> tuple[str, str]:
    return (
        urlsafe_base64_encode(force_bytes(user.pk)),
        default_token_generator.make_token(user),
    )


@pytest.mark.django_db
def test_returns_204_and_updates_password_on_valid_token() -> None:
    user = UserFactory()
    uid, token = _token_for(user)
    client = APIClient()

    response = client.post(
        URL,
        {"uid": uid, "token": token, "password": NEW_PASSWORD},
        format="json",
    )
    user.refresh_from_db()

    assert response.status_code == 204
    assert user.check_password(NEW_PASSWORD)


@pytest.mark.django_db
def test_returns_422_on_invalid_token() -> None:
    user = UserFactory()
    uid, _ = _token_for(user)
    client = APIClient()

    response = client.post(
        URL,
        {"uid": uid, "token": "garbage-token", "password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["type"].endswith("invalid_reset_token")


@pytest.mark.django_db
def test_returns_400_on_weak_password() -> None:
    user = UserFactory()
    uid, token = _token_for(user)
    client = APIClient()

    response = client.post(
        URL,
        {"uid": uid, "token": token, "password": "Aa1!"},  # too short
        format="json",
    )

    assert response.status_code == 400
    assert "password" in response.json().get("errors", {})
