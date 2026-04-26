"""Tests for POST /api/v1/auth/email-verification/request/."""

from __future__ import annotations

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/email-verification/request/"


@pytest.mark.django_db
def test_returns_204_and_sends_email_for_signed_in_user() -> None:
    user = UserFactory(email="user@example.com", email_verified_at=None)
    client = APIClient()
    client.force_login(user)

    response = client.post(URL, {}, format="json")

    assert response.status_code == 204
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["user@example.com"]


@pytest.mark.django_db
def test_returns_401_for_anonymous_request() -> None:
    response = APIClient().post(URL, {}, format="json")

    assert response.status_code == 401
    assert mail.outbox == []
