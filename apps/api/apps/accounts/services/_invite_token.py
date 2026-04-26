"""Internal helpers — invite token generation + lookup.

Plaintext invite tokens are URL-safe random strings (``secrets.token_urlsafe``).
The plaintext lives in the email link and only that link; the database
stores the SHA-256 hex digest. Single-use is enforced by ``accepted_at``
and ``revoked_at`` columns on ``Invite``.
"""

from __future__ import annotations

import hashlib
import secrets

from django.utils.encoding import force_bytes

INVITE_TOKEN_BYTES = 32  # ~43 url-safe characters once base64 encoded


def generate_invite_token() -> str:
    """Return a fresh URL-safe plaintext invite token."""
    return secrets.token_urlsafe(INVITE_TOKEN_BYTES)


def hash_invite_token(token: str) -> str:
    """SHA-256 hex digest of the plaintext token."""
    return hashlib.sha256(force_bytes(token)).hexdigest()
