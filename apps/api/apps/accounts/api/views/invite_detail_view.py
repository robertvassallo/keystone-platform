"""View — DELETE /api/v1/invites/<uuid>/ (revoke)."""

from __future__ import annotations

from uuid import UUID

from config.authentication import SessionAuth
from config.permissions import IsStaff
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.exceptions import InvalidInviteState
from apps.accounts.models import Invite, User
from apps.accounts.services import revoke_invite

from ._errors import InvalidInviteStateError


class InviteDetailView(APIView):
    """Revoke a pending invite — staff-only, scoped to caller's tenant."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsStaff,)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="invites_revoke",
    )
    def delete(self, request: Request, invite_id: UUID) -> Response:
        user = request.user
        assert isinstance(user, User)

        try:
            invite = Invite.objects.get(pk=invite_id, tenant_id=user.tenant_id)
        except Invite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            revoke_invite(invite=invite, revoked_by=user)
        except InvalidInviteState as exc:
            raise InvalidInviteStateError() from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
