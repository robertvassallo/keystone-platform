"""Tests for the update_profile service."""

from __future__ import annotations

import pytest

from apps.accounts.services import update_profile
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_sets_first_and_last_name() -> None:
    user = UserFactory(first_name="", last_name="")

    update_profile(user=user, first_name="Alice", last_name="Anderson")

    user.refresh_from_db()
    assert user.first_name == "Alice"
    assert user.last_name == "Anderson"


@pytest.mark.django_db
def test_trims_whitespace_around_each_field() -> None:
    user = UserFactory(first_name="", last_name="")

    update_profile(user=user, first_name="  Alice  ", last_name="\tAnderson\n")

    user.refresh_from_db()
    assert user.first_name == "Alice"
    assert user.last_name == "Anderson"


@pytest.mark.django_db
def test_none_argument_leaves_field_alone() -> None:
    user = UserFactory(first_name="Existing", last_name="")

    update_profile(user=user, last_name="Anderson")

    user.refresh_from_db()
    assert user.first_name == "Existing"
    assert user.last_name == "Anderson"


@pytest.mark.django_db
def test_empty_string_clears_field() -> None:
    user = UserFactory(first_name="Old", last_name="Name")

    update_profile(user=user, first_name="", last_name="")

    user.refresh_from_db()
    assert user.first_name == ""
    assert user.last_name == ""


@pytest.mark.django_db
def test_caps_each_field_at_max_length() -> None:
    user = UserFactory(first_name="", last_name="")
    very_long = "a" * 500

    update_profile(user=user, first_name=very_long)

    user.refresh_from_db()
    assert len(user.first_name) == 150


@pytest.mark.django_db
def test_no_args_does_not_save() -> None:
    user = UserFactory(first_name="Stable", last_name="Name")
    user.refresh_from_db()
    original_updated_at = user.updated_at

    update_profile(user=user)

    user.refresh_from_db()
    assert user.first_name == "Stable"
    assert user.updated_at == original_updated_at
