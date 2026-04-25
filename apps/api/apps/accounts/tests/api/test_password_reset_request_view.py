"""Tests for POST /api/v1/auth/password-reset/request/."""

from __future__ import annotations

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/password-reset/request/"


@pytest.mark.django_db
def test_returns_204_and_sends_email_for_known_user() -> None:
    UserFactory(email="known@example.com")
    client = APIClient()

    response = client.post(URL, {"email": "known@example.com"}, format="json")

    assert response.status_code == 204
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_returns_204_silently_for_unknown_email() -> None:
    client = APIClient()

    response = client.post(URL, {"email": "ghost@example.com"}, format="json")

    assert response.status_code == 204
    assert mail.outbox == []


@pytest.mark.django_db
def test_returns_400_on_invalid_email_format() -> None:
    client = APIClient()

    response = client.post(URL, {"email": "not-an-email"}, format="json")

    assert response.status_code == 400
    assert "email" in response.json().get("errors", {})
