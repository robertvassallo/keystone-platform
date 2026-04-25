"""View — GET /api/v1/users/<uuid:id>/."""

from __future__ import annotations

from uuid import UUID

from config.authentication import SessionAuth
from config.permissions import IsStaff
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import UserDetailSerializer
from apps.accounts.models import User
from apps.accounts.selectors import get_user_by_id


class UserDetailView(APIView):
    """Read-only detail view for a single user — staff only."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsStaff,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: UserDetailSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        operation_id="users_detail",
    )
    def get(self, request: Request, id: UUID) -> Response:  # noqa: A002
        viewer = request.user
        assert isinstance(viewer, User)
        target = get_user_by_id(user_id=id, tenant_id=viewer.tenant_id)
        if target is None:
            raise NotFound("User not found.")
        return Response(UserDetailSerializer(target).data, status=status.HTTP_200_OK)
