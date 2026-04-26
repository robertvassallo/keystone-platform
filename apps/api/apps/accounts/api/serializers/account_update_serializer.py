"""Serializer — partial update of the signed-in user's tenant."""

from __future__ import annotations

from rest_framework import serializers

MAX_NAME_LENGTH = 200
MAX_SLUG_LENGTH = 100


class AccountUpdateSerializer(serializers.Serializer[None]):
    """Whitelist of fields the tenant owner may PATCH on ``/account/``."""

    name = serializers.CharField(
        required=False,
        max_length=MAX_NAME_LENGTH,
        trim_whitespace=False,
    )
    slug = serializers.CharField(
        required=False,
        max_length=MAX_SLUG_LENGTH,
        trim_whitespace=False,
    )
