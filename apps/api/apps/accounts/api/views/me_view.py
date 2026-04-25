"""View — GET /api/v1/auth/me/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import UserSerializer
from apps.accounts.models import User


class MeView(APIView):
    """Return the currently signed-in user."""

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        operation_id="auth_me",
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)  # IsAuthenticated guarantees this
        return Response(UserSerializer(user).data)
