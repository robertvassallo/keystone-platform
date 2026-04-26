"""Serializer — partial update of the signed-in user's profile."""

from __future__ import annotations

from rest_framework import serializers

MAX_NAME_LENGTH = 150


class MeUpdateSerializer(serializers.Serializer[None]):
    """Whitelist of fields a user may PATCH on their own ``/me/`` resource."""

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_NAME_LENGTH,
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_NAME_LENGTH,
    )
