"""Domain exceptions for the accounts app.

Views map these to HTTP status codes per ``docs/01_architecture/api-conventions.md``.
"""

from __future__ import annotations


class AuthError(Exception):
    """Base class for accounts/auth domain errors."""


class DuplicateEmail(AuthError):
    """Raised when sign-up finds an existing user with the same email."""


class WeakPassword(AuthError):
    """Raised when ``AUTH_PASSWORD_VALIDATORS`` rejects a candidate password."""

    def __init__(self, messages: list[str]) -> None:
        super().__init__("; ".join(messages) if messages else "Password is too weak.")
        self.messages = messages


class InvalidCredentials(AuthError):
    """Raised when sign-in cannot authenticate the supplied email + password.

    Intentionally does **not** distinguish wrong password from unknown
    email or inactive account — surfacing that would leak whether an
    account exists.
    """


class InvalidResetToken(AuthError):
    """Raised when a password-reset token is missing, malformed, expired, or already used."""


class InvalidVerificationToken(AuthError):
    """Raised when an email-verification token is missing, malformed, or expired."""


class InvalidInviteToken(AuthError):
    """Raised when an invite token is missing, malformed, expired, used, or revoked."""


class InvalidInviteState(AuthError):
    """Raised when an invite cannot transition from its current state."""


class DuplicateInvite(AuthError):
    """Raised when a pending invite already exists for the (tenant, email)."""


class DuplicateMember(AuthError):
    """Raised when invite-send sees a User already exists for the email."""


class DuplicateSlug(AuthError):
    """Raised when a tenant rename collides with another tenant's slug."""


class InvalidSlug(AuthError):
    """Raised when a slug fails the format check (regex / non-empty)."""


class WrongCurrentPassword(AuthError):
    """Raised when ``change_password`` receives a wrong ``current_password``."""


class MFAAlreadyEnrolled(AuthError):
    """Raised when MFA setup is requested but the user already has a confirmed device."""


class MFANotEnrolled(AuthError):
    """Raised when an MFA-only operation is attempted without an enrolled device."""


class InvalidMFACode(AuthError):
    """Raised when a submitted MFA code (TOTP or recovery) does not validate."""


class MFAChallengeExpired(AuthError):
    """Raised when no partial-auth ticket is present, or it's older than the TTL."""
