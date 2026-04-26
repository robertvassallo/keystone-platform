"""View — GET / POST /api/v1/invites/."""

from __future__ import annotations

from config.authentication import SessionAuth
from config.permissions import IsTenantOwnerOrStaff
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    InviteCreateSerializer,
    InviteSerializer,
)
from apps.accounts.exceptions import DuplicateInvite, DuplicateMember
from apps.accounts.models import User
from apps.accounts.selectors import InviteStatus, list_invites
from apps.accounts.services import send_invite

from ._audit import audit_context_from_request
from ._errors import DuplicateInviteError, DuplicateMemberError


def _parse_status(raw: str | None) -> InviteStatus | None:
    if not raw:
        return None
    try:
        return InviteStatus(raw)
    except ValueError:
        return None


class InvitesListCreateView(APIView):
    """List or create invites — staff-only, scoped to the caller's tenant."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsTenantOwnerOrStaff,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: InviteSerializer(many=True),
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        operation_id="invites_list",
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)
        invites = list_invites(
            tenant_id=user.tenant_id,
            status=_parse_status(request.query_params.get("status")),
        )
        return Response({"data": InviteSerializer(invites, many=True).data})

    @extend_schema(
        request=InviteCreateSerializer,
        responses={
            status.HTTP_201_CREATED: InviteSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="invites_create",
    )
    def post(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)

        serializer = InviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invite = send_invite(
                tenant=user.tenant,
                email=serializer.validated_data["email"],
                invited_by=user,
                audit_context=audit_context_from_request(request),
            )
        except DuplicateMember as exc:
            raise DuplicateMemberError() from exc
        except DuplicateInvite as exc:
            raise DuplicateInviteError() from exc

        return Response(
            InviteSerializer(invite).data,
            status=status.HTTP_201_CREATED,
        )
