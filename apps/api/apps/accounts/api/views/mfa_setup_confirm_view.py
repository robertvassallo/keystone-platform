"""View — POST /api/v1/auth/mfa/setup/confirm/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    MFARecoveryCodesResponseSerializer,
    MFASetupConfirmSerializer,
)
from apps.accounts.exceptions import (
    InvalidMFACode,
    MFAAlreadyEnrolled,
    MFANotEnrolled,
)
from apps.accounts.models import User
from apps.accounts.services import confirm_mfa_setup

from ._audit import audit_context_from_request
from ._errors import (
    InvalidMFACodeError,
    MFAAlreadyEnrolledError,
    MFANotEnrolledError,
)


class MFASetupConfirmView(APIView):
    """Confirm MFA enrolment with a TOTP code; return one-time recovery codes."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=MFASetupConfirmSerializer,
        responses={
            status.HTTP_200_OK: MFARecoveryCodesResponseSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_mfa_setup_confirm",
    )
    def post(self, request: Request) -> Response:
        serializer = MFASetupConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        assert isinstance(user, User)

        try:
            codes = confirm_mfa_setup(
                user=user,
                code=serializer.validated_data["code"],
                audit_context=audit_context_from_request(request),
            )
        except MFAAlreadyEnrolled as exc:
            raise MFAAlreadyEnrolledError() from exc
        except MFANotEnrolled as exc:
            raise MFANotEnrolledError() from exc
        except InvalidMFACode as exc:
            raise InvalidMFACodeError() from exc

        return Response(
            {"recovery_codes": codes},
            status=status.HTTP_200_OK,
        )
