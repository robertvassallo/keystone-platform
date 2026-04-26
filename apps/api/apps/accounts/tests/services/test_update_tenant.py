"""Tests for the update_tenant service."""

from __future__ import annotations

import pytest

from apps.accounts.exceptions import DuplicateSlug, InvalidSlug
from apps.accounts.services import update_tenant
from apps.accounts.tests.factories import AccountFactory


@pytest.mark.django_db
def test_renames_name() -> None:
    tenant = AccountFactory(name="Old", slug="old")

    update_tenant(tenant=tenant, name="New Co")

    tenant.refresh_from_db()
    assert tenant.name == "New Co"
    assert tenant.slug == "old"


@pytest.mark.django_db
def test_lowercases_and_saves_slug() -> None:
    tenant = AccountFactory(slug="acme")

    update_tenant(tenant=tenant, slug="NewSlug-2026")

    tenant.refresh_from_db()
    assert tenant.slug == "newslug-2026"


@pytest.mark.django_db
def test_trims_whitespace_around_each_field() -> None:
    tenant = AccountFactory()

    update_tenant(tenant=tenant, name="  Trimmed  ", slug="  trimmed-slug  ")

    tenant.refresh_from_db()
    assert tenant.name == "Trimmed"
    assert tenant.slug == "trimmed-slug"


@pytest.mark.django_db
def test_none_argument_leaves_field_alone() -> None:
    tenant = AccountFactory(name="Stable", slug="stable")

    update_tenant(tenant=tenant, name="Renamed")

    tenant.refresh_from_db()
    assert tenant.name == "Renamed"
    assert tenant.slug == "stable"


@pytest.mark.django_db
def test_empty_name_is_rejected() -> None:
    tenant = AccountFactory()

    with pytest.raises(InvalidSlug):
        update_tenant(tenant=tenant, name="   ")


@pytest.mark.django_db
def test_invalid_slug_with_leading_hyphen() -> None:
    tenant = AccountFactory()

    with pytest.raises(InvalidSlug):
        update_tenant(tenant=tenant, slug="-leading-hyphen")


@pytest.mark.django_db
def test_invalid_slug_with_underscore() -> None:
    tenant = AccountFactory()

    with pytest.raises(InvalidSlug):
        update_tenant(tenant=tenant, slug="under_score")


@pytest.mark.django_db
def test_invalid_slug_empty() -> None:
    tenant = AccountFactory()

    with pytest.raises(InvalidSlug):
        update_tenant(tenant=tenant, slug="   ")


@pytest.mark.django_db
def test_duplicate_slug_raises_against_other_tenant() -> None:
    AccountFactory(slug="taken")
    mine = AccountFactory(slug="mine")

    with pytest.raises(DuplicateSlug):
        update_tenant(tenant=mine, slug="taken")


@pytest.mark.django_db
def test_setting_slug_to_current_value_is_allowed() -> None:
    tenant = AccountFactory(slug="acme")

    update_tenant(tenant=tenant, slug="acme")

    tenant.refresh_from_db()
    assert tenant.slug == "acme"
