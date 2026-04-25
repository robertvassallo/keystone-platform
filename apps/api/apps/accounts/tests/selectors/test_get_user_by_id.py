"""Tests for the get_user_by_id selector."""

from __future__ import annotations

from uuid import uuid4

import pytest

from apps.accounts.selectors import get_user_by_id
from apps.accounts.tests.factories import AccountFactory, UserFactory


@pytest.mark.django_db
def test_returns_the_user_when_found_in_their_tenant() -> None:
    user = UserFactory()

    result = get_user_by_id(user_id=user.pk, tenant_id=user.tenant_id)

    assert result is not None
    assert result.pk == user.pk


@pytest.mark.django_db
def test_returns_none_for_unknown_id() -> None:
    user = UserFactory()

    result = get_user_by_id(user_id=uuid4(), tenant_id=user.tenant_id)

    assert result is None


@pytest.mark.django_db
def test_returns_none_for_soft_deleted_user() -> None:
    user = UserFactory()
    user.soft_delete()

    result = get_user_by_id(user_id=user.pk, tenant_id=user.tenant_id)

    assert result is None


@pytest.mark.django_db
def test_returns_none_for_user_in_a_different_tenant() -> None:
    user = UserFactory()
    other_tenant = AccountFactory()

    result = get_user_by_id(user_id=user.pk, tenant_id=other_tenant.pk)

    assert result is None
