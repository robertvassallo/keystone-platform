"""Tests for the send_invite service."""

from __future__ import annotations

import pytest
from django.core import mail

from apps.accounts.exceptions import DuplicateInvite, DuplicateMember
from apps.accounts.models import Invite
from apps.accounts.services import send_invite
from apps.accounts.tests.factories import AccountFactory, UserFactory


@pytest.mark.django_db(transaction=True)
def test_creates_pending_invite_and_sends_email() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)

    invite = send_invite(
        tenant=tenant,
        email="newhire@example.com",
        invited_by=inviter,
    )

    assert invite.email == "newhire@example.com"
    assert invite.tenant_id == tenant.pk
    assert invite.token_hash != ""
    assert invite.accepted_at is None
    assert invite.revoked_at is None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["newhire@example.com"]
    assert "/accept-invite?" in mail.outbox[0].body


@pytest.mark.django_db
def test_lowercases_email() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)

    invite = send_invite(
        tenant=tenant,
        email="MIXED@Case.COM",
        invited_by=inviter,
    )

    assert invite.email == "mixed@case.com"


@pytest.mark.django_db
def test_raises_duplicate_member_when_user_exists() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    UserFactory(email="taken@example.com")

    with pytest.raises(DuplicateMember):
        send_invite(tenant=tenant, email="taken@example.com", invited_by=inviter)


@pytest.mark.django_db
def test_raises_duplicate_invite_for_pending_in_same_tenant() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    send_invite(tenant=tenant, email="newhire@example.com", invited_by=inviter)

    with pytest.raises(DuplicateInvite):
        send_invite(
            tenant=tenant,
            email="newhire@example.com",
            invited_by=inviter,
        )


@pytest.mark.django_db
def test_other_tenant_can_invite_same_email() -> None:
    tenant_a = AccountFactory()
    tenant_b = AccountFactory()
    inviter_a = UserFactory(is_staff=True, tenant=tenant_a)
    inviter_b = UserFactory(is_staff=True, tenant=tenant_b)

    send_invite(tenant=tenant_a, email="popular@example.com", invited_by=inviter_a)
    send_invite(tenant=tenant_b, email="popular@example.com", invited_by=inviter_b)

    assert Invite.objects.filter(email="popular@example.com").count() == 2
