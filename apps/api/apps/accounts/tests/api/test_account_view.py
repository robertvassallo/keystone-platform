"""Tests for GET /api/v1/account/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AccountFactory, UserFactory

URL = "/api/v1/account/"


@pytest.mark.django_db
def test_returns_200_with_signed_in_users_tenant() -> None:
    tenant = AccountFactory(name="Acme", slug="acme")
    user = UserFactory(email="me@example.com", tenant=tenant)
    client = APIClient()
    client.force_login(user)

    response = client.get(URL)
    body = response.json()

    assert response.status_code == 200
    assert body["id"] == str(tenant.pk)
    assert body["name"] == "Acme"
    assert body["slug"] == "acme"
    assert body["owner_email"] == "me@example.com"


@pytest.mark.django_db
def test_returns_401_for_anonymous_request() -> None:
    response = APIClient().get(URL)

    assert response.status_code == 401
