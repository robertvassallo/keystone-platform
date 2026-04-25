"""Tests for the confirm_password_reset service."""

from __future__ import annotations

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from apps.accounts.exceptions import InvalidResetToken, WeakPassword
from apps.accounts.models import User
from apps.accounts.services import confirm_password_reset
from apps.accounts.tests.factories import UserFactory

NEW_PASSWORD = "Brand-New-Password-2026"


def _token_for(user: User) -> tuple[str, str]:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


@pytest.mark.django_db
def test_confirm_password_reset_sets_new_password_and_returns_user() -> None:
    user = UserFactory()
    uidb64, token = _token_for(user)

    result = confirm_password_reset(
        uidb64=uidb64,
        token=token,
        new_password=NEW_PASSWORD,
    )

    user.refresh_from_db()
    assert result.pk == user.pk
    assert user.check_password(NEW_PASSWORD)


@pytest.mark.django_db
def test_confirm_password_reset_raises_on_garbage_uid() -> None:
    UserFactory()

    with pytest.raises(InvalidResetToken):
        confirm_password_reset(
            uidb64="not-a-valid-uid",
            token="any",
            new_password=NEW_PASSWORD,
        )


@pytest.mark.django_db
def test_confirm_password_reset_raises_on_invalid_token() -> None:
    user = UserFactory()
    uidb64, _ = _token_for(user)

    with pytest.raises(InvalidResetToken):
        confirm_password_reset(
            uidb64=uidb64,
            token="invalid-token-string",
            new_password=NEW_PASSWORD,
        )


@pytest.mark.django_db
def test_confirm_password_reset_raises_on_expired_token() -> None:
    user = UserFactory()
    with freeze_time("2026-04-25 12:00:00"):
        uidb64, token = _token_for(user)

    # PASSWORD_RESET_TIMEOUT = 3600s; advance > 1 hour.
    with freeze_time("2026-04-25 13:30:00"), pytest.raises(InvalidResetToken):
        confirm_password_reset(
            uidb64=uidb64,
            token=token,
            new_password=NEW_PASSWORD,
        )


@pytest.mark.django_db
def test_confirm_password_reset_raises_on_weak_password() -> None:
    user = UserFactory()
    uidb64, token = _token_for(user)

    with pytest.raises(WeakPassword):
        confirm_password_reset(
            uidb64=uidb64,
            token=token,
            new_password="short",
        )


@pytest.mark.django_db
def test_confirm_password_reset_token_is_single_use() -> None:
    user = UserFactory()
    uidb64, token = _token_for(user)

    confirm_password_reset(uidb64=uidb64, token=token, new_password=NEW_PASSWORD)

    # Reusing the same token after a successful reset is rejected because
    # the token-generator's hash includes the password.
    with pytest.raises(InvalidResetToken):
        confirm_password_reset(
            uidb64=uidb64,
            token=token,
            new_password="Different-Password-9876",
        )
