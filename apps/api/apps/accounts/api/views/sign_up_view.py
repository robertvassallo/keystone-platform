"""View — POST /api/v1/auth/sign-up/."""

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

from apps.accounts.api.serializers import SignUpSerializer, UserSerializer
from apps.accounts.exceptions import DuplicateEmail, WeakPassword
from apps.accounts.services import sign_up

from ._errors import DuplicateEmailError


class SignUpView(APIView):
    """Create a new user account.

    Throttled at the ``auth`` scope (5/min/IP) per
    ``docs/01_architecture/security.md``.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=SignUpSerializer,
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_sign_up",
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = sign_up(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except DuplicateEmail as exc:
            raise DuplicateEmailError() from exc
        except WeakPassword as exc:
            raise ValidationError({"password": exc.messages}) from exc

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )
