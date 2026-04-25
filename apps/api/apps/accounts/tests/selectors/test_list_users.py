"""Tests for the list_users selector."""

from __future__ import annotations

import pytest

from apps.accounts.selectors import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    UserStatus,
    list_users,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory


@pytest.mark.django_db
def test_returns_default_page_with_total_count() -> None:
    account = AccountFactory()
    UserFactory.create_batch(3, tenant=account)

    rows, total = list_users(
        tenant_id=account.pk,
        page=1,
        page_size=DEFAULT_PAGE_SIZE,
    )

    assert total == 3
    assert len(rows) == 3


@pytest.mark.django_db
def test_orders_newest_first_by_created_at() -> None:
    account = AccountFactory()
    first = UserFactory(email="first@example.com", tenant=account)
    middle = UserFactory(email="middle@example.com", tenant=account)
    newest = UserFactory(email="newest@example.com", tenant=account)

    rows, _ = list_users(
        tenant_id=account.pk,
        page=1,
        page_size=DEFAULT_PAGE_SIZE,
    )

    assert [u.pk for u in rows] == [newest.pk, middle.pk, first.pk]


@pytest.mark.django_db
def test_paginates_across_pages() -> None:
    account = AccountFactory()
    UserFactory.create_batch(5, tenant=account)

    page1, total1 = list_users(tenant_id=account.pk, page=1, page_size=2)
    page2, total2 = list_users(tenant_id=account.pk, page=2, page_size=2)
    page3, total3 = list_users(tenant_id=account.pk, page=3, page_size=2)

    assert total1 == total2 == total3 == 5
    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1


@pytest.mark.django_db
def test_clamps_page_size_to_max() -> None:
    account = AccountFactory()
    UserFactory.create_batch(2, tenant=account)

    rows, total = list_users(
        tenant_id=account.pk,
        page=1,
        page_size=MAX_PAGE_SIZE * 4,
    )

    assert len(rows) == 2
    assert total == 2


@pytest.mark.django_db
def test_clamps_page_below_one_to_one() -> None:
    account = AccountFactory()
    UserFactory(tenant=account)
    other = UserFactory(tenant=account)

    rows_neg, _ = list_users(tenant_id=account.pk, page=-5, page_size=10)
    rows_one, _ = list_users(tenant_id=account.pk, page=1, page_size=10)

    assert [u.pk for u in rows_neg] == [u.pk for u in rows_one]
    assert other.pk in {u.pk for u in rows_neg}


@pytest.mark.django_db
def test_returns_empty_for_page_past_data() -> None:
    account = AccountFactory()
    UserFactory.create_batch(3, tenant=account)

    rows, total = list_users(tenant_id=account.pk, page=99, page_size=10)

    assert rows == []
    assert total == 3


@pytest.mark.django_db
def test_excludes_users_in_a_different_tenant() -> None:
    own = AccountFactory()
    other = AccountFactory()
    UserFactory.create_batch(2, tenant=own)
    UserFactory.create_batch(3, tenant=other)

    rows, total = list_users(tenant_id=own.pk, page=1, page_size=DEFAULT_PAGE_SIZE)

    assert total == 2
    assert all(u.tenant_id == own.pk for u in rows)


@pytest.mark.django_db
def test_q_filter_matches_email_case_insensitively() -> None:
    account = AccountFactory()
    UserFactory(email="alice@example.com", tenant=account)
    UserFactory(email="bob@example.com", tenant=account)
    UserFactory(email="carol@example.com", tenant=account)

    rows, total = list_users(tenant_id=account.pk, q="ALICE")

    assert total == 1
    assert [u.email for u in rows] == ["alice@example.com"]


@pytest.mark.django_db
def test_q_substring_matches_anywhere_in_email() -> None:
    account = AccountFactory()
    UserFactory(email="alice@acme.com", tenant=account)
    UserFactory(email="bob@acme.com", tenant=account)
    UserFactory(email="carol@other.com", tenant=account)

    rows, total = list_users(tenant_id=account.pk, q="acme")

    assert total == 2
    assert {u.email for u in rows} == {"alice@acme.com", "bob@acme.com"}


@pytest.mark.django_db
def test_q_whitespace_is_trimmed_and_empty_q_is_ignored() -> None:
    account = AccountFactory()
    UserFactory(email="alice@example.com", tenant=account)
    UserFactory(email="bob@example.com", tenant=account)

    _, total_blank = list_users(tenant_id=account.pk, q="   ")
    rows_padded, total_padded = list_users(tenant_id=account.pk, q="  alice  ")

    assert total_blank == 2
    assert total_padded == 1
    assert [u.email for u in rows_padded] == ["alice@example.com"]


@pytest.mark.django_db
def test_status_active_returns_only_active_users() -> None:
    account = AccountFactory()
    UserFactory(email="active@example.com", is_active=True, tenant=account)
    UserFactory(email="dormant@example.com", is_active=False, tenant=account)

    rows, total = list_users(tenant_id=account.pk, status=UserStatus.ACTIVE)

    assert total == 1
    assert [u.email for u in rows] == ["active@example.com"]


@pytest.mark.django_db
def test_status_inactive_returns_only_inactive_users() -> None:
    account = AccountFactory()
    UserFactory(email="active@example.com", is_active=True, tenant=account)
    UserFactory(email="dormant@example.com", is_active=False, tenant=account)

    rows, total = list_users(tenant_id=account.pk, status=UserStatus.INACTIVE)

    assert total == 1
    assert [u.email for u in rows] == ["dormant@example.com"]


@pytest.mark.django_db
def test_status_staff_returns_only_staff_users() -> None:
    account = AccountFactory()
    UserFactory(email="member@example.com", is_staff=False, tenant=account)
    UserFactory(email="admin@example.com", is_staff=True, tenant=account)

    rows, total = list_users(tenant_id=account.pk, status=UserStatus.STAFF)

    assert total == 1
    assert [u.email for u in rows] == ["admin@example.com"]


@pytest.mark.django_db
def test_q_and_status_compose_with_and() -> None:
    account = AccountFactory()
    UserFactory(email="alice@acme.com", is_active=True, tenant=account)
    UserFactory(email="alice@other.com", is_active=False, tenant=account)
    UserFactory(email="bob@acme.com", is_active=False, tenant=account)

    rows, total = list_users(
        tenant_id=account.pk,
        q="alice",
        status=UserStatus.ACTIVE,
    )

    assert total == 1
    assert [u.email for u in rows] == ["alice@acme.com"]


@pytest.mark.django_db
def test_no_match_returns_zero_with_empty_rows() -> None:
    account = AccountFactory()
    UserFactory(email="alice@example.com", tenant=account)

    rows, total = list_users(tenant_id=account.pk, q="zzz-no-such-user")

    assert rows == []
    assert total == 0
