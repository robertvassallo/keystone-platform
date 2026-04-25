"""Test settings — fast hashing, in-memory cache, no DEBUG."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
