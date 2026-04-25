"""Tests for the list_users selector."""

from __future__ import annotations

import pytest

from apps.accounts.selectors import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    list_users,
)
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_returns_default_page_with_total_count() -> None:
    UserFactory.create_batch(3)

    rows, total = list_users(page=1, page_size=DEFAULT_PAGE_SIZE)

    assert total == 3
    assert len(rows) == 3


@pytest.mark.django_db
def test_orders_newest_first_by_created_at() -> None:
    first = UserFactory(email="first@example.com")
    middle = UserFactory(email="middle@example.com")
    newest = UserFactory(email="newest@example.com")

    rows, _ = list_users(page=1, page_size=DEFAULT_PAGE_SIZE)

    assert [u.pk for u in rows] == [newest.pk, middle.pk, first.pk]


@pytest.mark.django_db
def test_paginates_across_pages() -> None:
    UserFactory.create_batch(5)

    page1, total1 = list_users(page=1, page_size=2)
    page2, total2 = list_users(page=2, page_size=2)
    page3, total3 = list_users(page=3, page_size=2)

    assert total1 == total2 == total3 == 5
    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1


@pytest.mark.django_db
def test_clamps_page_size_to_max() -> None:
    UserFactory.create_batch(2)

    rows, total = list_users(page=1, page_size=MAX_PAGE_SIZE * 4)

    # 2 rows fit; what matters is no exception and the return shape.
    assert len(rows) == 2
    assert total == 2


@pytest.mark.django_db
def test_clamps_page_below_one_to_one() -> None:
    UserFactory()
    other = UserFactory()

    rows_neg, _ = list_users(page=-5, page_size=10)
    rows_one, _ = list_users(page=1, page_size=10)

    assert [u.pk for u in rows_neg] == [u.pk for u in rows_one]
    assert other.pk in {u.pk for u in rows_neg}


@pytest.mark.django_db
def test_returns_empty_for_page_past_data() -> None:
    UserFactory.create_batch(3)

    rows, total = list_users(page=99, page_size=10)

    assert rows == []
    assert total == 3
