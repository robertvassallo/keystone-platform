"""View — POST /api/v1/auth/mfa/recovery-codes/regenerate/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    MFAPasswordConfirmSerializer,
    MFARecoveryCodesResponseSerializer,
)
from apps.accounts.exceptions import MFANotEnrolled, WrongCurrentPassword
from apps.accounts.models import User
from apps.accounts.services import regenerate_recovery_codes

from ._audit import audit_context_from_request
from ._errors import MFANotEnrolledError, WrongCurrentPasswordError


class MFARegenerateRecoveryCodesView(APIView):
    """Replace the user's recovery codes — returns the new plaintext set once."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=MFAPasswordConfirmSerializer,
        responses={
            status.HTTP_200_OK: MFARecoveryCodesResponseSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_mfa_recovery_codes_regenerate",
    )
    def post(self, request: Request) -> Response:
        serializer = MFAPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        assert isinstance(user, User)

        try:
            codes = regenerate_recovery_codes(
                user=user,
                current_password=serializer.validated_data["current_password"],
                audit_context=audit_context_from_request(request),
            )
        except WrongCurrentPassword as exc:
            raise WrongCurrentPasswordError() from exc
        except MFANotEnrolled as exc:
            raise MFANotEnrolledError() from exc

        return Response(
            {"recovery_codes": codes},
            status=status.HTTP_200_OK,
        )
