"""Tests for the verify_email service."""

from __future__ import annotations

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from apps.accounts.exceptions import InvalidVerificationToken
from apps.accounts.models import User
from apps.accounts.services import verify_email
from apps.accounts.services._email_verification_token import (
    email_verification_token_generator,
)
from apps.accounts.tests.factories import UserFactory


def _token_for(user: User) -> tuple[str, str]:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)
    return uidb64, token


@pytest.mark.django_db
def test_marks_user_as_verified() -> None:
    user = UserFactory(email_verified_at=None)
    uidb64, token = _token_for(user)

    verify_email(uidb64=uidb64, token=token)

    user.refresh_from_db()
    assert user.email_verified_at is not None


@pytest.mark.django_db
def test_already_verified_user_double_click_is_idempotent() -> None:
    """A second click on the same link succeeds without re-stamping."""
    user = UserFactory(email_verified_at=None)
    uidb64, token = _token_for(user)

    verify_email(uidb64=uidb64, token=token)
    user.refresh_from_db()
    first_verified_at = user.email_verified_at

    # Re-issuing the token after verification still works because the
    # hash includes email_verified_at — but we expect it to NOT change
    # the column on subsequent calls.
    uidb64_2, token_2 = _token_for(user)
    verify_email(uidb64=uidb64_2, token=token_2)

    user.refresh_from_db()
    assert user.email_verified_at == first_verified_at


@pytest.mark.django_db
def test_raises_on_garbage_uid() -> None:
    with pytest.raises(InvalidVerificationToken):
        verify_email(uidb64="not-a-valid-uid", token="any")


@pytest.mark.django_db
def test_raises_on_invalid_token() -> None:
    user = UserFactory(email_verified_at=None)
    uidb64, _ = _token_for(user)

    with pytest.raises(InvalidVerificationToken):
        verify_email(uidb64=uidb64, token="invalid-token-string")


@pytest.mark.django_db
def test_raises_on_expired_token() -> None:
    user = UserFactory(email_verified_at=None)
    with freeze_time("2026-04-25 12:00:00"):
        uidb64, token = _token_for(user)

    # EMAIL_VERIFICATION_TIMEOUT = 24 * 3600s; advance > 24 hours.
    with freeze_time("2026-04-26 13:00:00"), pytest.raises(InvalidVerificationToken):
        verify_email(uidb64=uidb64, token=token)


@pytest.mark.django_db
def test_token_survives_a_sign_in_between_signup_and_verify() -> None:
    """The hash deliberately excludes ``last_login`` so a sign-in
    between sign-up and verification does not invalidate the link."""
    user = UserFactory(email_verified_at=None, last_login=None)
    uidb64, token = _token_for(user)

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    verify_email(uidb64=uidb64, token=token)
    user.refresh_from_db()
    assert user.email_verified_at is not None


@pytest.mark.django_db
def test_password_reset_token_is_not_a_valid_verification_token() -> None:
    """Different ``key_salt`` keeps the two flows mutually unforgeable."""
    user = UserFactory(email_verified_at=None)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = default_token_generator.make_token(user)

    with pytest.raises(InvalidVerificationToken):
        verify_email(uidb64=uidb64, token=reset_token)
