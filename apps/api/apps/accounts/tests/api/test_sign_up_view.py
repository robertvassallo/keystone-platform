"""Tests for POST /api/v1/auth/sign-up/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD

URL = "/api/v1/auth/sign-up/"


@pytest.mark.django_db
def test_sign_up_returns_201_and_serialized_user_on_success() -> None:
    client = APIClient()

    response = client.post(
        URL,
        {"email": "new@example.com", "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "password" not in body
    assert User.objects.filter(email="new@example.com").exists()


@pytest.mark.django_db
def test_sign_up_returns_400_problem_details_on_invalid_email() -> None:
    client = APIClient()

    response = client.post(
        URL,
        {"email": "not-an-email", "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert body["type"].startswith("about:blank#")
    assert "email" in body.get("errors", {})


@pytest.mark.django_db
def test_sign_up_returns_422_when_email_is_already_registered() -> None:
    client = APIClient()
    client.post(
        URL,
        {"email": "dup@example.com", "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    response = client.post(
        URL,
        {"email": "DUP@example.com", "password": DEFAULT_TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["type"].endswith("duplicate_email")
