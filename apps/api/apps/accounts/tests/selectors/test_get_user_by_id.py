"""Tests for the get_user_by_id selector."""

from __future__ import annotations

from uuid import uuid4

import pytest

from apps.accounts.selectors import get_user_by_id
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_returns_the_user_when_found() -> None:
    user = UserFactory()

    result = get_user_by_id(user_id=user.pk)

    assert result is not None
    assert result.pk == user.pk


@pytest.mark.django_db
def test_returns_none_for_unknown_id() -> None:
    UserFactory()

    result = get_user_by_id(user_id=uuid4())

    assert result is None


@pytest.mark.django_db
def test_returns_none_for_soft_deleted_user() -> None:
    user = UserFactory()
    user.soft_delete()

    result = get_user_by_id(user_id=user.pk)

    assert result is None
