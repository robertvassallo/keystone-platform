"""Tests for POST /api/v1/auth/email-verification/confirm/."""

from __future__ import annotations

import pytest
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services._email_verification_token import (
    email_verification_token_generator,
)
from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/email-verification/confirm/"


def _token_for(user: User) -> tuple[str, str]:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)
    return uidb64, token


@pytest.mark.django_db
def test_returns_204_and_marks_user_verified() -> None:
    user = UserFactory(email_verified_at=None)
    uidb64, token = _token_for(user)
    client = APIClient()

    response = client.post(URL, {"uid": uidb64, "token": token}, format="json")

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.email_verified_at is not None


@pytest.mark.django_db
def test_returns_422_on_garbage_token() -> None:
    user = UserFactory(email_verified_at=None)
    uidb64, _ = _token_for(user)
    client = APIClient()

    response = client.post(URL, {"uid": uidb64, "token": "garbage"}, format="json")

    body = response.json()
    assert response.status_code == 422
    assert body["type"].endswith("invalid_verification_token")


@pytest.mark.django_db
def test_returns_400_on_missing_fields() -> None:
    client = APIClient()

    response = client.post(URL, {}, format="json")

    assert response.status_code == 400
    body = response.json()
    assert "uid" in body.get("errors", {})
    assert "token" in body.get("errors", {})
