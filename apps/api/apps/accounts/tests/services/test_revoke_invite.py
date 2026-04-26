"""Tests for the revoke_invite service."""

from __future__ import annotations

import pytest
from django.utils import timezone

from apps.accounts.exceptions import InvalidInviteState
from apps.accounts.models import Invite
from apps.accounts.services import revoke_invite
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory


def _create_pending_invite(tenant, inviter):  # type: ignore[no-untyped-def]
    return Invite.objects.create(
        tenant=tenant,
        email="new@example.com",
        invited_by=inviter,
        token_hash=hash_invite_token(generate_invite_token()),
    )


@pytest.mark.django_db
def test_marks_pending_invite_revoked() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    invite = _create_pending_invite(tenant, inviter)

    revoke_invite(invite=invite, revoked_by=inviter)

    invite.refresh_from_db()
    assert invite.revoked_at is not None
    assert invite.revoked_by_id == inviter.pk


@pytest.mark.django_db
def test_raises_when_already_accepted() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    accepted_user = UserFactory(tenant=tenant)
    invite = _create_pending_invite(tenant, inviter)
    invite.accepted_at = timezone.now()
    invite.accepted_by = accepted_user
    invite.save(update_fields=["accepted_at", "accepted_by"])

    with pytest.raises(InvalidInviteState):
        revoke_invite(invite=invite, revoked_by=inviter)


@pytest.mark.django_db
def test_raises_when_already_revoked() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    invite = _create_pending_invite(tenant, inviter)
    invite.revoked_at = timezone.now()
    invite.save(update_fields=["revoked_at"])

    with pytest.raises(InvalidInviteState):
        revoke_invite(invite=invite, revoked_by=inviter)
