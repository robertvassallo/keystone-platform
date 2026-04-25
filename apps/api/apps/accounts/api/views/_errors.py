"""HTTP-mapping for accounts domain exceptions.

Views translate the domain errors into these DRF exceptions; the project's
RFC 7807 handler (``config.exception_handler``) reshapes the body.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed


class DuplicateEmailError(APIException):
    """422 — sign-up rejected because an active account exists."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Email is already registered."
    default_code = "duplicate_email"


class InvalidCredentialsError(AuthenticationFailed):
    """401 — sign-in rejected; intentionally vague to avoid account leaks."""

    default_detail = "Email or password is incorrect."
    default_code = "invalid_credentials"


class InvalidResetTokenError(APIException):
    """422 — password-reset token is missing, malformed, expired, or used."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "This password-reset link is invalid or has expired."
    default_code = "invalid_reset_token"


class WrongCurrentPasswordError(APIException):
    """422 — change-password supplied an incorrect current password."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Current password is incorrect."
    default_code = "wrong_current_password"
