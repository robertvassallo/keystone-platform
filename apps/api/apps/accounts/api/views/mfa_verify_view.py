"""View — POST /api/v1/auth/mfa/verify/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import MFAVerifySerializer, UserSerializer
from apps.accounts.exceptions import InvalidMFACode, MFAChallengeExpired
from apps.accounts.services import verify_mfa_challenge

from ._errors import InvalidMFACodeError, MFAChallengeExpiredError


class MFAVerifyView(APIView):
    """Complete sign-in by verifying the partial-auth ticket + MFA code.

    Anonymous + ``auth``-scope throttle (5/min/IP). The user's ticket
    lives in ``request.session`` from a prior successful sign-in step.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=MFAVerifySerializer,
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_mfa_verify",
    )
    def post(self, request: Request) -> Response:
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = verify_mfa_challenge(
                request=request._request,
                code=serializer.validated_data["code"],
            )
        except MFAChallengeExpired as exc:
            raise MFAChallengeExpiredError() from exc
        except InvalidMFACode as exc:
            raise InvalidMFACodeError() from exc

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
