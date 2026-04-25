"""Tests for the change_password service."""

from __future__ import annotations

from importlib import import_module

import pytest
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpRequest
from django.test import RequestFactory

from apps.accounts.exceptions import WeakPassword, WrongCurrentPassword
from apps.accounts.services import change_password
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory

NEW_PASSWORD = "Even-Stronger-Password-2026"


def _request_with_session(rf: RequestFactory) -> HttpRequest:
    request = rf.post("/")
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore  # noqa: N806
    request.session = SessionStore()
    return request


@pytest.mark.django_db
def test_change_password_updates_hash_and_keeps_session_alive() -> None:
    user = UserFactory()
    rf = RequestFactory()
    request = _request_with_session(rf)
    request.user = user  # normally set by AuthenticationMiddleware
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    initial_hash = request.session.get("_auth_user_hash")

    change_password(
        request=request,
        user=user,
        current_password=DEFAULT_TEST_PASSWORD,
        new_password=NEW_PASSWORD,
    )
    user.refresh_from_db()

    assert user.check_password(NEW_PASSWORD)
    assert "_auth_user_id" in request.session  # session not invalidated
    assert request.session.get("_auth_user_hash") != initial_hash


@pytest.mark.django_db
def test_change_password_raises_on_wrong_current_password() -> None:
    user = UserFactory()
    rf = RequestFactory()
    request = _request_with_session(rf)

    with pytest.raises(WrongCurrentPassword):
        change_password(
            request=request,
            user=user,
            current_password="not-the-real-password",
            new_password=NEW_PASSWORD,
        )

    user.refresh_from_db()
    assert user.check_password(DEFAULT_TEST_PASSWORD)  # unchanged


@pytest.mark.django_db
def test_change_password_raises_on_weak_new_password() -> None:
    user = UserFactory()
    rf = RequestFactory()
    request = _request_with_session(rf)

    with pytest.raises(WeakPassword):
        change_password(
            request=request,
            user=user,
            current_password=DEFAULT_TEST_PASSWORD,
            new_password="short",
        )
