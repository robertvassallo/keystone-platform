"""View — GET / PATCH /api/v1/account/."""

from __future__ import annotations

from config.authentication import SessionAuth
from config.permissions import IsTenantOwnerOrStaff
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    AccountSerializer,
    AccountUpdateSerializer,
)
from apps.accounts.exceptions import DuplicateSlug, InvalidSlug
from apps.accounts.models import User
from apps.accounts.services import update_tenant

from ._errors import DuplicateSlugError


class AccountView(APIView):
    """Read or partially-update the signed-in user's tenant.

    GET — any authenticated user (read their own tenant).
    PATCH — owner of the tenant or platform staff.
    """

    authentication_classes = (SessionAuth,)

    def get_permissions(self):  # type: ignore[no-untyped-def]
        """Choose permission class per HTTP method."""
        if self.request.method == "PATCH":
            return [IsTenantOwnerOrStaff()]
        return [IsAuthenticated()]

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

    @extend_schema(
        request=AccountUpdateSerializer,
        responses={
            status.HTTP_200_OK: AccountSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="account_update",
    )
    def patch(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)

        serializer = AccountUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            update_tenant(
                tenant=user.tenant,
                name=serializer.validated_data.get("name"),
                slug=serializer.validated_data.get("slug"),
            )
        except InvalidSlug as exc:
            raise ValidationError({"slug": [str(exc)]}) from exc
        except DuplicateSlug as exc:
            raise DuplicateSlugError() from exc

        return Response(AccountSerializer(user.tenant).data)
