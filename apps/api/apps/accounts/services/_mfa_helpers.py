"""Internal helpers shared by the MFA services."""

from __future__ import annotations

import base64
import hashlib
import io
import secrets

import qrcode
from django.utils.encoding import force_bytes

# Recovery-code alphabet — uppercase letters and digits, dropping the
# visually-ambiguous characters (0/O, 1/I) so users can copy them by hand
# without misreading.
RECOVERY_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
RECOVERY_CODE_LENGTH = 8
RECOVERY_CODE_COUNT = 10


def generate_recovery_codes(count: int = RECOVERY_CODE_COUNT) -> list[str]:
    """Return ``count`` fresh single-use recovery codes."""
    return [
        "".join(
            secrets.choice(RECOVERY_CODE_ALPHABET)
            for _ in range(RECOVERY_CODE_LENGTH)
        )
        for _ in range(count)
    ]


def hash_recovery_code(code: str) -> str:
    """Hash a recovery code with SHA-256 and return its hex digest."""
    return hashlib.sha256(force_bytes(code.upper())).hexdigest()


def make_qr_data_url(uri: str) -> str:
    """Render ``uri`` as a QR code; return a base64-encoded data URL."""
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def secret_from_device(bin_key: bytes) -> str:
    """Render a TOTPDevice's binary key as the base32 secret apps display."""
    return base64.b32encode(bin_key).decode("ascii").rstrip("=")
