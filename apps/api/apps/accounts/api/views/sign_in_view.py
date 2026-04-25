"""View — POST /api/v1/auth/sign-in/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import SignInSerializer, UserSerializer
from apps.accounts.exceptions import InvalidCredentials
from apps.accounts.services import sign_in

from ._errors import InvalidCredentialsError


class SignInView(APIView):
    """Authenticate the user and start a session.

    Throttled at the ``auth`` scope (5/min/IP) per
    ``docs/01_architecture/security.md``.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=SignInSerializer,
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_202_ACCEPTED: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        operation_id="auth_sign_in",
    )
    def post(self, request: Request) -> Response:
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = sign_in(
                request=request._request,
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                remember_me=serializer.validated_data["remember_me"],
            )
        except InvalidCredentials as exc:
            raise InvalidCredentialsError() from exc

        if user is None:
            return Response(
                {"mfa_required": True},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
