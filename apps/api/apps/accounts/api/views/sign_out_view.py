"""View — POST /api/v1/auth/sign-out/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import sign_out


class SignOutView(APIView):
    """End the current session.

    Idempotent — returns 204 whether or not a session existed.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        operation_id="auth_sign_out",
    )
    def post(self, request: Request) -> Response:
        sign_out(request=request._request)
        return Response(status=status.HTTP_204_NO_CONTENT)
