"""View — GET /api/v1/auth/invite/preview/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import InvitePreviewSerializer
from apps.accounts.exceptions import InvalidInviteToken
from apps.accounts.services import preview_invite

from ._errors import InvalidInviteTokenError


class InvitePreviewView(APIView):
    """Public read of an invite's metadata (tenant name, email, expiry)."""

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        responses={
            status.HTTP_200_OK: InvitePreviewSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_invite_preview",
    )
    def get(self, request: Request) -> Response:
        uid = request.query_params.get("uid", "")
        token = request.query_params.get("token", "")
        if not uid or not token:
            return Response(
                {"errors": {"uid": ["Required."], "token": ["Required."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            invite = preview_invite(uidb64=uid, token=token)
        except InvalidInviteToken as exc:
            raise InvalidInviteTokenError() from exc

        return Response(
            {
                "tenant_name": invite.tenant.name,
                "email": invite.email,
                "expires_at": invite.expires_at,
            },
        )
