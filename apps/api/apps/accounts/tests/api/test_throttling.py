"""Tests for the auth-scope throttle on sign-in / sign-up."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

URL = "/api/v1/auth/sign-in/"
ALLOWED_PER_MINUTE = 5


@pytest.mark.django_db
def test_sign_in_returns_429_after_five_attempts_per_minute() -> None:
    client = APIClient()
    payload = {"email": "ghost@example.com", "password": "any-password-1234"}

    for _ in range(ALLOWED_PER_MINUTE):
        response = client.post(URL, payload, format="json")
        assert response.status_code == 401  # invalid creds, but counted

    response = client.post(URL, payload, format="json")
    assert response.status_code == 429
    assert response.json()["status"] == 429
