"""Tests for the sign_out service."""

from __future__ import annotations

from importlib import import_module

import pytest
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpRequest
from django.test import RequestFactory

from apps.accounts.services import sign_out
from apps.accounts.tests.factories import DEFAULT_TEST_PASSWORD, UserFactory


def _request_with_session(rf: RequestFactory) -> HttpRequest:
    request = rf.post("/")
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore  # noqa: N806
    request.session = SessionStore()
    return request


@pytest.mark.django_db
def test_sign_out_clears_authenticated_session() -> None:
    user = UserFactory(password=DEFAULT_TEST_PASSWORD)
    rf = RequestFactory()
    request = _request_with_session(rf)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    assert "_auth_user_id" in request.session

    sign_out(request=request)

    assert "_auth_user_id" not in request.session


@pytest.mark.django_db
def test_sign_out_is_idempotent_when_no_session_exists() -> None:
    rf = RequestFactory()
    request = _request_with_session(rf)

    sign_out(request=request)  # must not raise

    assert "_auth_user_id" not in request.session
