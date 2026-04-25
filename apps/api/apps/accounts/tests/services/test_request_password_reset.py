"""Tests for the request_password_reset service."""

from __future__ import annotations

import pytest
from django.core import mail

from apps.accounts.services import request_password_reset
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_request_password_reset_sends_email_when_user_exists() -> None:
    user = UserFactory(email="user@example.com")

    request_password_reset(email=user.email)

    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.to == ["user@example.com"]
    assert "/reset-password?" in sent.body
    assert "uid=" in sent.body
    assert "token=" in sent.body


@pytest.mark.django_db
def test_request_password_reset_lowercases_email_before_lookup() -> None:
    UserFactory(email="user@example.com")

    request_password_reset(email="USER@EXAMPLE.com")

    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_request_password_reset_silent_for_unknown_email() -> None:
    request_password_reset(email="ghost@example.com")

    assert mail.outbox == []


@pytest.mark.django_db
def test_request_password_reset_silent_for_inactive_user() -> None:
    UserFactory(email="inactive@example.com", is_active=False)

    request_password_reset(email="inactive@example.com")

    assert mail.outbox == []
