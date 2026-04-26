"""Tests for the invites HTTP API."""

from __future__ import annotations

import pytest
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.accounts.models import Invite
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory

LIST_URL = "/api/v1/invites/"
PREVIEW_URL = "/api/v1/auth/invite/preview/"
ACCEPT_URL = "/api/v1/auth/invite/accept/"


def _create_invite(*, tenant, inviter, email="new@example.com"):  # type: ignore[no-untyped-def]
    plaintext = generate_invite_token()
    invite = Invite.objects.create(
        tenant=tenant,
        email=email,
        invited_by=inviter,
        token_hash=hash_invite_token(plaintext),
    )
    uidb64 = urlsafe_base64_encode(force_bytes(invite.pk))
    return invite, uidb64, plaintext


# ──────────────────────── POST /api/v1/invites/ ────────────────────────


@pytest.mark.django_db(transaction=True)
def test_post_invites_201_for_staff_user() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=tenant)
    client = APIClient()
    client.force_login(staff)

    response = client.post(LIST_URL, {"email": "new@example.com"}, format="json")
    body = response.json()

    assert response.status_code == 201
    assert body["email"] == "new@example.com"
    assert body["status"] == "pending"


@pytest.mark.django_db
def test_post_invites_403_for_non_staff() -> None:
    user = UserFactory(is_staff=False)
    client = APIClient()
    client.force_login(user)

    response = client.post(LIST_URL, {"email": "x@y.com"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_post_invites_401_for_anonymous() -> None:
    response = APIClient().post(LIST_URL, {"email": "x@y.com"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_post_invites_422_when_user_already_exists() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=tenant)
    UserFactory(email="taken@example.com")
    client = APIClient()
    client.force_login(staff)

    response = client.post(LIST_URL, {"email": "taken@example.com"}, format="json")
    body = response.json()

    assert response.status_code == 422
    assert body["type"].endswith("duplicate_member")


# ──────────────────────── GET /api/v1/invites/ ────────────────────────


@pytest.mark.django_db
def test_get_invites_lists_only_caller_tenant() -> None:
    own_tenant = AccountFactory()
    other_tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=own_tenant)
    own_inviter = UserFactory(is_staff=True, tenant=own_tenant)
    other_inviter = UserFactory(is_staff=True, tenant=other_tenant)

    _create_invite(tenant=own_tenant, inviter=own_inviter, email="ours@example.com")
    _create_invite(tenant=other_tenant, inviter=other_inviter, email="theirs@example.com")

    client = APIClient()
    client.force_login(staff)

    response = client.get(LIST_URL)
    body = response.json()

    assert response.status_code == 200
    assert {row["email"] for row in body["data"]} == {"ours@example.com"}


# ──────────────────────── DELETE /api/v1/invites/<id>/ ────────────────────────


@pytest.mark.django_db
def test_delete_invite_204_for_pending_in_own_tenant() -> None:
    tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=tenant)
    invite, _, _ = _create_invite(tenant=tenant, inviter=staff)
    client = APIClient()
    client.force_login(staff)

    response = client.delete(f"{LIST_URL}{invite.pk}/")
    invite.refresh_from_db()

    assert response.status_code == 204
    assert invite.revoked_at is not None


@pytest.mark.django_db
def test_delete_invite_404_for_other_tenant_invite() -> None:
    own_tenant = AccountFactory()
    other_tenant = AccountFactory()
    staff = UserFactory(is_staff=True, tenant=own_tenant)
    other_inviter = UserFactory(is_staff=True, tenant=other_tenant)
    invite, _, _ = _create_invite(tenant=other_tenant, inviter=other_inviter)
    client = APIClient()
    client.force_login(staff)

    response = client.delete(f"{LIST_URL}{invite.pk}/")

    assert response.status_code == 404


# ──────────────────── GET /api/v1/auth/invite/preview/ ────────────────────


@pytest.mark.django_db
def test_preview_returns_metadata_for_valid_token() -> None:
    tenant = AccountFactory(name="Acme Co")
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, token = _create_invite(tenant=tenant, inviter=inviter)

    response = APIClient().get(PREVIEW_URL, {"uid": uid, "token": token})
    body = response.json()

    assert response.status_code == 200
    assert body["tenant_name"] == "Acme Co"
    assert body["email"] == "new@example.com"


@pytest.mark.django_db
def test_preview_422_for_garbage_token() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, _ = _create_invite(tenant=tenant, inviter=inviter)

    response = APIClient().get(PREVIEW_URL, {"uid": uid, "token": "garbage"})

    assert response.status_code == 422


@pytest.mark.django_db
def test_preview_400_for_missing_params() -> None:
    response = APIClient().get(PREVIEW_URL)
    assert response.status_code == 400


# ──────────────────── POST /api/v1/auth/invite/accept/ ────────────────────


@pytest.mark.django_db(transaction=True)
def test_accept_creates_user_and_signs_in() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, token = _create_invite(tenant=tenant, inviter=inviter)

    response = APIClient().post(
        ACCEPT_URL,
        {"uid": uid, "token": token, "password": "Strong-Password-7531"},
        format="json",
    )
    body = response.json()

    assert response.status_code == 201
    assert body["email"] == "new@example.com"
    assert body["tenant"]["id"] == str(tenant.pk)


@pytest.mark.django_db
def test_accept_422_for_garbage_token() -> None:
    response = APIClient().post(
        ACCEPT_URL,
        {"uid": "x", "token": "y", "password": "Strong-Password-7531"},
        format="json",
    )
    assert response.status_code == 422
