"""View — POST /api/v1/auth/mfa/setup/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import MFASetupResponseSerializer
from apps.accounts.exceptions import MFAAlreadyEnrolled
from apps.accounts.models import User
from apps.accounts.services import start_mfa_setup

from ._errors import MFAAlreadyEnrolledError


class MFASetupStartView(APIView):
    """Begin MFA enrolment — returns the secret + QR for the user to scan."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: MFASetupResponseSerializer,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_mfa_setup_start",
    )
    def post(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)

        try:
            payload = start_mfa_setup(user=user)
        except MFAAlreadyEnrolled as exc:
            raise MFAAlreadyEnrolledError() from exc

        return Response(payload, status=status.HTTP_200_OK)
