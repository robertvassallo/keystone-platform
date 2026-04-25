"""View — POST /api/v1/auth/email-verification/confirm/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import EmailVerificationConfirmSerializer
from apps.accounts.exceptions import InvalidVerificationToken
from apps.accounts.services import verify_email

from ._errors import InvalidVerificationTokenError


class EmailVerificationConfirmView(APIView):
    """Mark the user's email verified using uid + token from the email link."""

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=EmailVerificationConfirmSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_email_verification_confirm",
    )
    def post(self, request: Request) -> Response:
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            verify_email(
                uidb64=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
            )
        except InvalidVerificationToken as exc:
            raise InvalidVerificationTokenError() from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
