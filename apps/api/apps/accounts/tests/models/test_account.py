"""Tests for the Account model."""

from __future__ import annotations

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.models import Account
from apps.accounts.tests.factories import AccountFactory


@pytest.mark.django_db
def test_creates_account_with_uuid_v7_id_and_audit_columns() -> None:
    account = AccountFactory(name="Acme")

    assert account.id is not None
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.deleted_at is None
    assert str(account) == "Acme"


@pytest.mark.django_db
def test_unique_slug_constraint_among_active_accounts() -> None:
    AccountFactory(slug="duplicate-slug")

    with pytest.raises(IntegrityError):
        AccountFactory(slug="duplicate-slug")


@pytest.mark.django_db
def test_soft_deleted_account_does_not_block_slug_reuse() -> None:
    deleted = AccountFactory(slug="reusable")
    deleted.deleted_at = timezone.now()
    deleted.save(update_fields=["deleted_at", "updated_at"])

    # Same slug can be reused once the prior holder is soft-deleted.
    fresh = Account.objects.create(name="Fresh", slug="reusable")

    assert fresh.pk != deleted.pk
