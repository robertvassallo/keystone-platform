"""Token generator for email-verification links.

Subclasses ``PasswordResetTokenGenerator`` so we get the same battle-tested
HMAC + base36-timestamp shape, but with two key differences:

1. The hash value excludes ``user.password`` and ``user.last_login`` —
   neither should invalidate a verification link. Specifically, a fresh
   signup signs in (updating ``last_login``) before clicking the link,
   and we don't want that sign-in to nuke the email already in their
   inbox. The hash includes ``user.email_verified_at`` instead, so a
   successful verification *does* invalidate outstanding tokens.

2. ``check_token`` uses ``settings.EMAIL_VERIFICATION_TIMEOUT`` (24 h
   default) instead of ``PASSWORD_RESET_TIMEOUT`` (1 h). Verification
   emails tolerate more delivery delay than reset links.

Same base secret as the framework default, but with an overridden
``key_salt`` so a token from one flow cannot be replayed against the
other.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

from apps.accounts.models import User


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Stateless one-time tokens for verifying a user's email."""

    key_salt = "apps.accounts.services._email_verification_token"

    def _make_hash_value(self, user: User, timestamp: int) -> str:
        verified = (
            ""
            if user.email_verified_at is None
            else user.email_verified_at.replace(microsecond=0, tzinfo=None).isoformat()
        )
        return f"{user.pk}{user.email}{verified}{timestamp}"

    def check_token(self, user: User | None, token: str | None) -> bool:
        if not (user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False
        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            return False
        timeout = int(getattr(settings, "EMAIL_VERIFICATION_TIMEOUT", 24 * 3600))
        return self._num_seconds(self._now()) - ts <= timeout


email_verification_token_generator = EmailVerificationTokenGenerator()
