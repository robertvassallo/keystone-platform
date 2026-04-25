"""View — GET /api/v1/account/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import AccountSerializer
from apps.accounts.models import User


class AccountView(APIView):
    """Return the signed-in user's tenant."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: AccountSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        operation_id="account_get",
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)
        return Response(
            AccountSerializer(user.tenant).data,
            status=status.HTTP_200_OK,
        )
