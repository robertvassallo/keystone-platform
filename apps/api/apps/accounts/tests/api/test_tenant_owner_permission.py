"""Verify the IsTenantOwnerOrStaff gate on the four protected views.

The existing per-view test files already cover the staff-allowed +
anonymous-blocked + non-staff-blocked paths. This file fills the gap:
the new path where a non-staff user *is* the tenant owner and should
get access, plus the explicit non-owner-non-staff member-of-tenant
case.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account, Invite
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory


def _make_owner(tenant: Account):  # type: ignore[no-untyped-def]
    """Return a non-staff User who owns ``tenant``."""
    owner = UserFactory(is_staff=False, tenant=tenant)
    tenant.owner = owner
    tenant.save(update_fields=["owner"])
    return owner


def _make_member(tenant: Account):  # type: ignore[no-untyped-def]
    """Return a non-staff User in ``tenant`` who is *not* the owner."""
    return UserFactory(is_staff=False, tenant=tenant)


# ───────────────────── /api/v1/users/ ─────────────────────


@pytest.mark.django_db
def test_users_list_200_for_tenant_owner_who_is_not_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.get("/api/v1/users/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_users_list_403_for_member_who_is_not_owner_or_staff() -> None:
    tenant = AccountFactory()
    _make_owner(tenant)
    member = _make_member(tenant)
    client = APIClient()
    client.force_login(member)

    response = client.get("/api/v1/users/")

    assert response.status_code == 403


# ───────────────────── /api/v1/invites/ ─────────────────────


@pytest.mark.django_db(transaction=True)
def test_invites_post_201_for_tenant_owner_who_is_not_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.post(
        "/api/v1/invites/",
        {"email": "newhire@example.com"},
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_invites_post_403_for_member_who_is_not_owner_or_staff() -> None:
    tenant = AccountFactory()
    _make_owner(tenant)
    member = _make_member(tenant)
    client = APIClient()
    client.force_login(member)

    response = client.post(
        "/api/v1/invites/",
        {"email": "x@y.com"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_invites_get_200_for_tenant_owner_who_is_not_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.get("/api/v1/invites/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_invites_delete_204_for_tenant_owner_who_is_not_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    invite = Invite.objects.create(
        tenant=tenant,
        email="new@example.com",
        invited_by=owner,
        token_hash=hash_invite_token(generate_invite_token()),
    )
    client = APIClient()
    client.force_login(owner)

    response = client.delete(f"/api/v1/invites/{invite.pk}/")

    assert response.status_code == 204


# ───────────────────── /api/v1/users/<id>/ ─────────────────────


@pytest.mark.django_db
def test_user_detail_200_for_tenant_owner_who_is_not_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    client = APIClient()
    client.force_login(owner)

    response = client.get(f"/api/v1/users/{owner.pk}/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_detail_403_for_member_who_is_not_owner_or_staff() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    member = _make_member(tenant)
    client = APIClient()
    client.force_login(member)

    response = client.get(f"/api/v1/users/{owner.pk}/")

    assert response.status_code == 403


# ───────────────────── /me/ exposes is_tenant_owner ─────────────────────


@pytest.mark.django_db
def test_me_payload_marks_owner_as_tenant_owner() -> None:
    tenant = AccountFactory()
    owner = _make_owner(tenant)
    client = APIClient()
    client.force_login(owner)

    body = client.get("/api/v1/auth/me/").json()

    assert body["is_tenant_owner"] is True
    assert body["is_staff"] is False


@pytest.mark.django_db
def test_me_payload_marks_member_as_not_owner() -> None:
    tenant = AccountFactory()
    _make_owner(tenant)
    member = _make_member(tenant)
    client = APIClient()
    client.force_login(member)

    body = client.get("/api/v1/auth/me/").json()

    assert body["is_tenant_owner"] is False


@pytest.mark.django_db
def test_sign_up_response_marks_signer_as_tenant_owner() -> None:
    """A fresh sign-up should land as owner of the tenant it just created."""
    response = APIClient().post(
        "/api/v1/auth/sign-up/",
        {"email": "alice@example.com", "password": "Strong-Password-7531"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 201
    assert body["is_tenant_owner"] is True
