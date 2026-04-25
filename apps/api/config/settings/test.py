"""Test settings — fast hashing, in-memory cache, no DEBUG."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Disable django-otp's per-device backoff in tests so wrong-code/correct-code
# sequences don't trip the 1-second cooldown (the cooldown is real for users
# but it makes deterministic tests painful).
OTP_TOTP_THROTTLE_FACTOR = 0
