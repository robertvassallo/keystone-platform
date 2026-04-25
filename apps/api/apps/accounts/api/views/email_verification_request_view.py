"""View — POST /api/v1/auth/email-verification/request/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.services import send_email_verification


class EmailVerificationRequestView(APIView):
    """Re-issue a verification email to the signed-in user.

    Authenticated; ``auth`` throttle scope (5/min/IP) caps any spam attempt
    a user might run against their own inbox. Returns ``204`` regardless
    of whether the user is already verified — re-sending to a verified
    user is a noop and we don't want this endpoint to leak verification
    state to a session-fixated attacker.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        operation_id="auth_email_verification_request",
    )
    def post(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)
        send_email_verification(user=user)
        return Response(status=status.HTTP_204_NO_CONTENT)
