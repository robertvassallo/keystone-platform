"""Tests for GET /api/v1/users/<uuid:id>/."""

from __future__ import annotations

from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory


def _detail_url(user_id: object) -> str:
    return f"/api/v1/users/{user_id}/"


@pytest.mark.django_db
def test_returns_200_with_full_payload_for_staff_user() -> None:
    staff = UserFactory(is_staff=True)
    target = UserFactory(email="target@example.com")
    client = APIClient()
    client.force_login(staff)

    response = client.get(_detail_url(target.pk))
    body = response.json()

    assert response.status_code == 200
    assert body["email"] == "target@example.com"
    # Detail shape includes the richer fields not in the list shape.
    assert {"is_superuser", "updated_at", "tenant_id"} <= set(body.keys())


@pytest.mark.django_db
def test_returns_403_for_authenticated_non_staff_user() -> None:
    target = UserFactory()
    other = UserFactory(is_staff=False)
    client = APIClient()
    client.force_login(other)

    response = client.get(_detail_url(target.pk))

    assert response.status_code == 403


@pytest.mark.django_db
def test_returns_401_for_anonymous_request() -> None:
    target = UserFactory()

    response = APIClient().get(_detail_url(target.pk))

    assert response.status_code == 401


@pytest.mark.django_db
def test_returns_404_for_unknown_id() -> None:
    staff = UserFactory(is_staff=True)
    client = APIClient()
    client.force_login(staff)

    response = client.get(_detail_url(uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_returns_404_for_soft_deleted_user() -> None:
    staff = UserFactory(is_staff=True)
    deleted = UserFactory()
    deleted.soft_delete()
    client = APIClient()
    client.force_login(staff)

    response = client.get(_detail_url(deleted.pk))

    assert response.status_code == 404
