"""Tests for PATCH /api/v1/auth/me/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

URL = "/api/v1/auth/me/"


@pytest.mark.django_db
def test_returns_200_with_updated_user_for_signed_in_user() -> None:
    user = UserFactory(first_name="", last_name="")
    client = APIClient()
    client.force_login(user)

    response = client.patch(
        URL,
        {"first_name": "Alice", "last_name": "Anderson"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 200
    assert body["first_name"] == "Alice"
    assert body["last_name"] == "Anderson"
    assert body["display_name"] == "Alice Anderson"


@pytest.mark.django_db
def test_partial_patch_only_updates_supplied_fields() -> None:
    user = UserFactory(first_name="Original", last_name="Surname")
    client = APIClient()
    client.force_login(user)

    response = client.patch(URL, {"first_name": "Renamed"}, format="json")
    body = response.json()

    assert response.status_code == 200
    assert body["first_name"] == "Renamed"
    assert body["last_name"] == "Surname"


@pytest.mark.django_db
def test_unknown_fields_are_silently_ignored() -> None:
    user = UserFactory(first_name="", last_name="", email="user@example.com")
    client = APIClient()
    client.force_login(user)

    response = client.patch(
        URL,
        {"first_name": "Alice", "is_staff": True, "email": "x@y.com"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 200
    assert body["is_staff"] is False
    assert body["email"] == "user@example.com"


@pytest.mark.django_db
def test_returns_400_on_oversized_first_name() -> None:
    user = UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.patch(URL, {"first_name": "a" * 200}, format="json")

    assert response.status_code == 400
    assert "first_name" in response.json().get("errors", {})


@pytest.mark.django_db
def test_returns_401_for_anonymous_request() -> None:
    response = APIClient().patch(URL, {"first_name": "Alice"}, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_display_name_falls_back_to_email_local_part_when_blank() -> None:
    user = UserFactory(
        email="alice@example.com",
        first_name="",
        last_name="",
    )
    client = APIClient()
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json()["display_name"] == "alice"
