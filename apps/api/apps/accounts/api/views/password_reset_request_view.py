"""View — POST /api/v1/auth/password-reset/request/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import PasswordResetRequestSerializer
from apps.accounts.services import request_password_reset


class PasswordResetRequestView(APIView):
    """Send a reset email if the address is registered.

    Returns ``204`` regardless of whether the email matched, to avoid
    account-enumeration via response shape or timing.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: None,
        },
        operation_id="auth_password_reset_request",
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_password_reset(email=serializer.validated_data["email"])

        return Response(status=status.HTTP_204_NO_CONTENT)
