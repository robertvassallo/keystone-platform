"""Tests for the verify_mfa_challenge service."""

from __future__ import annotations

from datetime import timedelta
from importlib import import_module

import pytest
from django.conf import settings
from django.http import HttpRequest
from django.test import RequestFactory
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.exceptions import InvalidMFACode, MFAChallengeExpired
from apps.accounts.models import MFARecoveryCode
from apps.accounts.services import verify_mfa_challenge
from apps.accounts.services._mfa_helpers import hash_recovery_code
from apps.accounts.services.mfa_verify_challenge import CHALLENGE_SESSION_KEY
from apps.accounts.tests._mfa_helpers import current_totp_code
from apps.accounts.tests.factories import UserFactory


def _request_with_session(rf: RequestFactory) -> HttpRequest:
    request = rf.post("/")
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore  # noqa: N806
    request.session = SessionStore()
    return request


def _ticket(*, user_id: str, remember_me: bool = False, ttl_minutes: int = 5) -> dict[str, object]:
    return {
        "user_id": user_id,
        "remember_me": remember_me,
        "expires_at": (
            timezone.now() + timedelta(minutes=ttl_minutes)
        ).isoformat(),
    }


@pytest.mark.django_db
def test_verify_with_valid_totp_clears_ticket_and_signs_in() -> None:
    user = UserFactory()
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    rf = RequestFactory()
    request = _request_with_session(rf)
    request.session[CHALLENGE_SESSION_KEY] = _ticket(user_id=str(user.pk))

    result = verify_mfa_challenge(request=request, code=current_totp_code(device))

    assert result.pk == user.pk
    assert CHALLENGE_SESSION_KEY not in request.session
    assert "_auth_user_id" in request.session


@pytest.mark.django_db
def test_verify_with_recovery_code_consumes_it() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    plaintext = "AAAA1111"
    MFARecoveryCode.objects.create(
        user=user, code_hash=hash_recovery_code(plaintext),
    )
    rf = RequestFactory()
    request = _request_with_session(rf)
    request.session[CHALLENGE_SESSION_KEY] = _ticket(user_id=str(user.pk))

    verify_mfa_challenge(request=request, code=plaintext)

    consumed = MFARecoveryCode.objects.get(user=user)
    assert consumed.consumed_at is not None


@pytest.mark.django_db
def test_verify_with_wrong_code_keeps_ticket_for_retry() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    rf = RequestFactory()
    request = _request_with_session(rf)
    ticket = _ticket(user_id=str(user.pk))
    request.session[CHALLENGE_SESSION_KEY] = ticket

    with pytest.raises(InvalidMFACode):
        verify_mfa_challenge(request=request, code="000000")

    assert request.session[CHALLENGE_SESSION_KEY] == ticket
    assert "_auth_user_id" not in request.session


@pytest.mark.django_db
def test_verify_without_session_ticket_raises_expired() -> None:
    rf = RequestFactory()
    request = _request_with_session(rf)

    with pytest.raises(MFAChallengeExpired):
        verify_mfa_challenge(request=request, code="123456")


@pytest.mark.django_db
def test_verify_with_past_expires_at_raises_expired_and_clears_ticket() -> None:
    user = UserFactory()
    TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    rf = RequestFactory()
    request = _request_with_session(rf)
    request.session[CHALLENGE_SESSION_KEY] = {
        "user_id": str(user.pk),
        "remember_me": False,
        "expires_at": (timezone.now() - timedelta(seconds=1)).isoformat(),
    }

    with pytest.raises(MFAChallengeExpired):
        verify_mfa_challenge(request=request, code="000000")

    assert CHALLENGE_SESSION_KEY not in request.session


@pytest.mark.django_db
def test_verify_honours_remember_me_from_ticket() -> None:
    user = UserFactory()
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    rf = RequestFactory()
    request = _request_with_session(rf)
    request.session[CHALLENGE_SESSION_KEY] = _ticket(
        user_id=str(user.pk), remember_me=True,
    )

    verify_mfa_challenge(request=request, code=current_totp_code(device))

    assert request.session.get_expiry_age() == settings.REMEMBER_ME_DURATION
