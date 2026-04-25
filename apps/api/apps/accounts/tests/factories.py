"""Factory Boy factories for the accounts app."""

from __future__ import annotations

from typing import Any

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Account, User

DEFAULT_TEST_PASSWORD = "Test-Password-1234567"


class AccountFactory(DjangoModelFactory[Account]):
    """Build a tenant Account.

    Default name + slug are sequenced so each call creates a fresh,
    non-colliding account. Tests that want multiple users in the same
    tenant should create one Account and pass ``tenant=...`` to the
    User factory.
    """

    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f"Test Account {n}")
    slug = factory.Sequence(lambda n: f"test-account-{n}")


class UserFactory(DjangoModelFactory[User]):
    """Build a User with a unique email, known password, and a fresh tenant.

    Pass ``tenant=existing_account`` to share a tenant across multiple
    users (the typical setup for ``/users`` list / detail tests). Pass
    ``password=...`` to override; otherwise ``DEFAULT_TEST_PASSWORD`` is
    used and accessible via ``user.check_password``.
    """

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_active = True
    tenant = factory.SubFactory(AccountFactory)

    @factory.post_generation
    def password(
        self: User,
        create: bool,
        extracted: str | None,
        **kwargs: Any,
    ) -> None:
        """Hash the password (the field default skips this)."""
        self.set_password(extracted or DEFAULT_TEST_PASSWORD)
        if create:
            self.save()
