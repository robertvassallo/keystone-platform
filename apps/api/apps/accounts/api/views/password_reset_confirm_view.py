"""View — POST /api/v1/auth/password-reset/confirm/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import PasswordResetConfirmSerializer
from apps.accounts.exceptions import InvalidResetToken, WeakPassword
from apps.accounts.services import confirm_password_reset

from ._errors import InvalidResetTokenError


class PasswordResetConfirmView(APIView):
    """Apply the new password if the reset token validates."""

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_password_reset_confirm",
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            confirm_password_reset(
                uidb64=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["password"],
            )
        except InvalidResetToken as exc:
            raise InvalidResetTokenError() from exc
        except WeakPassword as exc:
            raise ValidationError({"password": exc.messages}) from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
