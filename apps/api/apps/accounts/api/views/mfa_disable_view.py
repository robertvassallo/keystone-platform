"""View — POST /api/v1/auth/mfa/disable/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import MFAPasswordConfirmSerializer
from apps.accounts.exceptions import WrongCurrentPassword
from apps.accounts.models import User
from apps.accounts.services import disable_mfa

from ._errors import WrongCurrentPasswordError


class MFADisableView(APIView):
    """Tear down MFA after the user re-confirms with their password."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=MFAPasswordConfirmSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_mfa_disable",
    )
    def post(self, request: Request) -> Response:
        serializer = MFAPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        assert isinstance(user, User)

        try:
            disable_mfa(
                user=user,
                current_password=serializer.validated_data["current_password"],
            )
        except WrongCurrentPassword as exc:
            raise WrongCurrentPasswordError() from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
