"""Tests for the send_email_verification service."""

from __future__ import annotations

import pytest
from django.core import mail

from apps.accounts.services import send_email_verification
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_sends_email_to_active_user() -> None:
    user = UserFactory(email="user@example.com", email_verified_at=None)

    send_email_verification(user=user)

    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.to == ["user@example.com"]
    assert "/verify-email?" in sent.body
    assert "uid=" in sent.body
    assert "token=" in sent.body


@pytest.mark.django_db
def test_silent_for_inactive_user() -> None:
    user = UserFactory(email="dormant@example.com", is_active=False)

    send_email_verification(user=user)

    assert mail.outbox == []


@pytest.mark.django_db
def test_resending_to_already_verified_user_still_sends() -> None:
    """An already-verified user can still request a fresh link.

    The verify endpoint is a no-op on second click; the send endpoint
    therefore doesn't gate on verification state.
    """
    user = UserFactory()  # Factory default is verified.

    send_email_verification(user=user)

    assert len(mail.outbox) == 1
