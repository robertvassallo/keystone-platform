"""Factory Boy factories for the accounts app."""

from __future__ import annotations

from typing import Any

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import User

DEFAULT_TEST_PASSWORD = "Test-Password-1234567"


class UserFactory(DjangoModelFactory[User]):
    """Build a User with a unique email and a known password.

    Pass ``password=...`` to override; otherwise ``DEFAULT_TEST_PASSWORD``
    is used and accessible to assertions via ``user.check_password``.
    """

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_active = True

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
