"""Tests for GET /api/v1/audit/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.audit import AuditAction
from apps.accounts.services import record_audit_event
from apps.accounts.tests.factories import AccountFactory, UserFactory

URL = "/api/v1/audit/"


def _make_owner(tenant):  # type: ignore[no-untyped-def]
    owner = UserFactory(is_staff=False, tenant=tenant)
    tenant.owner = owner
    tenant.save(update_fields=["owner"])
    return owner


@pytest.mark.django_db
def test_returns_200_for_owner_with_paginated_body() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    record_audit_event(tenant=tenant, action=AuditAction.AUTH_SIGN_IN)
    record_audit_event(tenant=tenant, action=AuditAction.TENANT_RENAMED)

    client = APIClient()
    client.force_login(owner)

    response = client.get(URL)
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["total"] == 2
    actions = [row["action"] for row in body["data"]]
    # newest first
    assert actions == ["tenant.renamed", "auth.sign_in"]


@pytest.mark.django_db
def test_returns_403_for_member_who_is_not_owner_or_staff() -> None:
    tenant = AccountFactory()
    _make_owner(tenant)
    member = UserFactory(is_staff=False, tenant=tenant)

    client = APIClient()
    client.force_login(member)
    response = client.get(URL)

    assert response.status_code == 403


@pytest.mark.django_db
def test_returns_401_for_anonymous() -> None:
    response = APIClient().get(URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_excludes_other_tenants_events() -> None:
    own = AccountFactory()
    other = AccountFactory()
    owner = _make_owner(own)
    record_audit_event(tenant=own, action=AuditAction.AUTH_SIGN_IN)
    record_audit_event(tenant=other, action=AuditAction.AUTH_SIGN_IN)

    client = APIClient()
    client.force_login(owner)
    response = client.get(URL)
    body = response.json()

    assert body["page"]["total"] == 1


@pytest.mark.django_db
def test_pagination_page_and_page_size() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    for _ in range(5):
        record_audit_event(tenant=tenant, action=AuditAction.AUTH_SIGN_IN)

    client = APIClient()
    client.force_login(owner)
    response = client.get(URL, {"page": 2, "page_size": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["page"]["page"] == 2
    assert body["page"]["page_size"] == 2
    assert body["page"]["total"] == 5
    assert len(body["data"]) == 2
