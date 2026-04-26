"""Tests for PATCH /api/v1/account/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AccountFactory, UserFactory

URL = "/api/v1/account/"


def _owner_for(tenant):  # type: ignore[no-untyped-def]
    owner = UserFactory(is_staff=False, tenant=tenant)
    tenant.owner = owner
    tenant.save(update_fields=["owner"])
    return owner


@pytest.mark.django_db
def test_owner_can_rename_their_tenant() -> None:
    tenant = AccountFactory(name="Old", slug="old")
    owner = _owner_for(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.patch(
        URL,
        {"name": "New Co", "slug": "new-co"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "New Co"
    assert body["slug"] == "new-co"


@pytest.mark.django_db
def test_member_who_is_not_owner_gets_403() -> None:
    tenant = AccountFactory()
    _owner_for(tenant)
    member = UserFactory(is_staff=False, tenant=tenant)
    client = APIClient()
    client.force_login(member)

    response = client.patch(URL, {"name": "Mine"}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_request_returns_401() -> None:
    response = APIClient().patch(URL, {"name": "X"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_partial_patch_only_updates_supplied_fields() -> None:
    tenant = AccountFactory(name="Stable", slug="stable")
    owner = _owner_for(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.patch(URL, {"name": "Renamed"}, format="json")
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Renamed"
    assert body["slug"] == "stable"


@pytest.mark.django_db
def test_unknown_fields_are_silently_ignored() -> None:
    tenant = AccountFactory(name="Acme", slug="acme")
    owner = _owner_for(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.patch(
        URL,
        {"name": "Renamed", "owner_email": "x@y.com", "id": "123"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Renamed"
    assert body["owner_email"] == owner.email


@pytest.mark.django_db
def test_invalid_slug_returns_400() -> None:
    tenant = AccountFactory()
    owner = _owner_for(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.patch(URL, {"slug": "Has Spaces"}, format="json")
    body = response.json()

    assert response.status_code == 400
    assert "slug" in body.get("errors", {})


@pytest.mark.django_db
def test_duplicate_slug_returns_422() -> None:
    AccountFactory(slug="taken")
    mine = AccountFactory(slug="mine")
    owner = _owner_for(mine)
    client = APIClient()
    client.force_login(owner)

    response = client.patch(URL, {"slug": "taken"}, format="json")
    body = response.json()

    assert response.status_code == 422
    assert body["type"].endswith("duplicate_slug")


@pytest.mark.django_db
def test_get_unchanged_for_any_authenticated_user() -> None:
    tenant = AccountFactory()
    member = UserFactory(is_staff=False, tenant=tenant)
    client = APIClient()
    client.force_login(member)

    response = client.get(URL)

    assert response.status_code == 200
