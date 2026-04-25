"""Tests for the sign_up service."""

from __future__ import annotations

import pytest

from apps.accounts.exceptions import DuplicateEmail, WeakPassword
from apps.accounts.models import User
from apps.accounts.services import sign_up

STRONG_PASSWORD = "Reliable-Password-7531"


@pytest.mark.django_db
def test_sign_up_creates_user_with_lowercased_email() -> None:
    user = sign_up(email="MixedCase@Example.COM", password=STRONG_PASSWORD)

    assert isinstance(user, User)
    assert user.email == "mixedcase@example.com"
    assert user.check_password(STRONG_PASSWORD)
    assert user.is_active is True
    assert user.is_staff is False


@pytest.mark.django_db
def test_sign_up_raises_duplicate_email_on_second_registration() -> None:
    sign_up(email="user@example.com", password=STRONG_PASSWORD)

    with pytest.raises(DuplicateEmail):
        sign_up(email="USER@example.com", password=STRONG_PASSWORD)


@pytest.mark.django_db
def test_sign_up_raises_weak_password_when_too_short() -> None:
    with pytest.raises(WeakPassword) as excinfo:
        sign_up(email="short@example.com", password="abc12345")

    assert excinfo.value.messages


@pytest.mark.django_db
def test_sign_up_creates_a_tenant_for_the_new_user() -> None:
    user = sign_up(email="alice@example.com", password=STRONG_PASSWORD)

    assert user.tenant is not None
    assert user.tenant.slug == "alice"
    assert user.tenant.name.startswith("alice")


@pytest.mark.django_db
def test_sign_up_appends_a_collision_suffix_when_slug_taken() -> None:
    sign_up(email="bob@example.com", password=STRONG_PASSWORD)
    second = sign_up(email="bob@otherco.com", password=STRONG_PASSWORD)

    assert second.tenant.slug == "bob-2"
