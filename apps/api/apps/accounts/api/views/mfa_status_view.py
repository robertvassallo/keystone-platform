"""View — GET /api/v1/auth/mfa/status/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import MFAStatusResponseSerializer
from apps.accounts.models import User
from apps.accounts.services import get_mfa_status


class MFAStatusView(APIView):
    """Return whether MFA is enabled and how many recovery codes remain."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={status.HTTP_200_OK: MFAStatusResponseSerializer},
        operation_id="auth_mfa_status",
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)
        return Response(get_mfa_status(user=user))
