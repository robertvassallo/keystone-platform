"""Tests for GET /api/v1/users/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AccountFactory, UserFactory

URL = "/api/v1/users/"


@pytest.mark.django_db
def test_returns_200_with_paginated_body_for_staff_user() -> None:
    tenant = AccountFactory()
    staff = UserFactory(email="staff@example.com", is_staff=True, tenant=tenant)
    UserFactory.create_batch(2, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL)
    body = response.json()

    assert response.status_code == 200
    assert body["page"] == {"page": 1, "page_size": 25, "total": 3}
    assert len(body["data"]) == 3
    assert {row["email"] for row in body["data"]} >= {"staff@example.com"}


@pytest.mark.django_db
def test_excludes_users_in_a_different_tenant() -> None:
    own = AccountFactory()
    other = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=own)
    UserFactory.create_batch(2, tenant=own)
    UserFactory.create_batch(3, tenant=other)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL)
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 3
    assert all(row["email"] != UserFactory.email for row in body["data"])


@pytest.mark.django_db
def test_returns_403_for_authenticated_non_staff_user() -> None:
    user = UserFactory(is_staff=False)
    client = APIClient()
    client.force_login(user)

    response = client.get(URL)

    assert response.status_code == 403


@pytest.mark.django_db
def test_returns_401_for_anonymous_request() -> None:
    response = APIClient().get(URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_honours_page_and_page_size_query_params() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=tenant)
    UserFactory.create_batch(4, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"page": 2, "page_size": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["page"] == {"page": 2, "page_size": 2, "total": 5}
    assert len(body["data"]) == 2


@pytest.mark.django_db
def test_returns_empty_data_array_for_page_beyond_data() -> None:
    staff = UserFactory(is_staff=True)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"page": 99})
    body = response.json()

    assert response.status_code == 200
    assert body["data"] == []
    assert body["page"]["total"] == 1


@pytest.mark.django_db
def test_q_query_param_filters_by_email_substring() -> None:
    tenant = AccountFactory()
    staff = UserFactory(email="staff@example.com", is_staff=True, tenant=tenant)
    UserFactory(email="alice@example.com", tenant=tenant)
    UserFactory(email="bob@other.com", tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"q": "alice"})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 1
    assert [row["email"] for row in body["data"]] == ["alice@example.com"]


@pytest.mark.django_db
def test_status_query_param_filters_to_staff_only() -> None:
    tenant = AccountFactory()
    staff = UserFactory(email="admin@example.com", is_staff=True, tenant=tenant)
    UserFactory.create_batch(2, is_staff=False, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"status": "staff"})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 1
    assert [row["email"] for row in body["data"]] == ["admin@example.com"]


@pytest.mark.django_db
def test_status_query_param_filters_to_inactive_only() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, is_active=True, tenant=tenant)
    UserFactory(email="dormant@example.com", is_active=False, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"status": "inactive"})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 1
    assert [row["email"] for row in body["data"]] == ["dormant@example.com"]


@pytest.mark.django_db
def test_unknown_status_value_is_ignored() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=tenant)
    UserFactory.create_batch(2, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"status": "garbage"})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 3


@pytest.mark.django_db
def test_q_and_status_compose() -> None:
    tenant = AccountFactory()
    staff = UserFactory(email="admin@acme.com", is_staff=True, tenant=tenant)
    UserFactory(email="alice@acme.com", is_staff=False, tenant=tenant)
    UserFactory(email="other@acme.com", is_staff=True, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.get(URL, {"q": "admin", "status": "staff"})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 1
    assert [row["email"] for row in body["data"]] == ["admin@acme.com"]
