"""Tests for the accept_invite service."""

from __future__ import annotations

import pytest
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from apps.accounts.exceptions import (
    DuplicateEmail,
    InvalidInviteToken,
    WeakPassword,
)
from apps.accounts.models import Account, Invite, User
from apps.accounts.services import accept_invite
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory

STRONG_PASSWORD = "Reliable-Password-7531"


def _make_invite_with_plaintext(
    *,
    tenant: Account,
    inviter: User,
    email: str = "new@example.com",
) -> tuple[Invite, str, str]:
    plaintext = generate_invite_token()
    invite = Invite.objects.create(
        tenant=tenant,
        email=email,
        invited_by=inviter,
        token_hash=hash_invite_token(plaintext),
    )
    uidb64 = urlsafe_base64_encode(force_bytes(invite.pk))
    return invite, uidb64, plaintext


@pytest.mark.django_db(transaction=True)
def test_creates_user_in_invite_tenant_and_marks_accepted() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    invite, uid, token = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    user = accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)

    invite.refresh_from_db()
    assert user.email == invite.email
    assert user.tenant_id == tenant.pk
    assert user.check_password(STRONG_PASSWORD)
    assert invite.accepted_at is not None
    assert invite.accepted_by_id == user.pk


@pytest.mark.django_db
def test_raises_invalid_token_for_garbage() -> None:
    with pytest.raises(InvalidInviteToken):
        accept_invite(uidb64="bogus", token="garbage", password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_raises_invalid_token_for_wrong_token() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, _ = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    with pytest.raises(InvalidInviteToken):
        accept_invite(uidb64=uid, token="wrong-token", password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_raises_invalid_token_when_already_accepted() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, token = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)

    with pytest.raises(InvalidInviteToken):
        accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_raises_invalid_token_when_revoked() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    invite, uid, token = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    invite.revoked_at = timezone.now()
    invite.save(update_fields=["revoked_at"])

    with pytest.raises(InvalidInviteToken):
        accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_raises_invalid_token_when_expired() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)

    with freeze_time("2026-04-26 00:00:00"):
        _, uid, token = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    # INVITE_TTL = 7 days; advance > 7 days.
    with freeze_time("2026-05-04 00:00:00"), pytest.raises(InvalidInviteToken):
        accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_raises_weak_password_for_short_password() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, token = _make_invite_with_plaintext(tenant=tenant, inviter=inviter)

    with pytest.raises(WeakPassword):
        accept_invite(uidb64=uid, token=token, password="short")


@pytest.mark.django_db
def test_raises_duplicate_email_when_user_appears_between_send_and_accept() -> None:
    tenant = AccountFactory()
    inviter = UserFactory(is_staff=True, tenant=tenant)
    _, uid, token = _make_invite_with_plaintext(
        tenant=tenant,
        inviter=inviter,
        email="racy@example.com",
    )

    UserFactory(email="racy@example.com")

    with pytest.raises(DuplicateEmail):
        accept_invite(uidb64=uid, token=token, password=STRONG_PASSWORD)
