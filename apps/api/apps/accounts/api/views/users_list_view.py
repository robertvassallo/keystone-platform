"""View — GET /api/v1/users/."""

from __future__ import annotations

from config.authentication import SessionAuth
from config.permissions import IsStaff
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import UserListItemSerializer
from apps.accounts.models import User
from apps.accounts.selectors import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MIN_PAGE,
    list_users,
)


def _parse_int(raw: str, default: int) -> int:
    """Parse a query-string int safely; fall back to ``default`` on garbage."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


class UsersListView(APIView):
    """Paginated read-only list of users — staff only."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsStaff,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        operation_id="users_list",
    )
    def get(self, request: Request) -> Response:
        page = max(_parse_int(request.query_params.get("page", ""), MIN_PAGE), MIN_PAGE)
        page_size = max(
            1,
            min(
                _parse_int(
                    request.query_params.get("page_size", ""),
                    DEFAULT_PAGE_SIZE,
                ),
                MAX_PAGE_SIZE,
            ),
        )

        user = request.user
        assert isinstance(user, User)
        rows, total = list_users(
            tenant_id=user.tenant_id,
            page=page,
            page_size=page_size,
        )

        return Response(
            {
                "data": UserListItemSerializer(rows, many=True).data,
                "page": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                },
            },
            status=status.HTTP_200_OK,
        )
