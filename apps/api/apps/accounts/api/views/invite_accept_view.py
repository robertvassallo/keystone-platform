"""View — POST /api/v1/auth/invite/accept/."""

from __future__ import annotations

from config.authentication import SessionAuth
from django.contrib.auth import login as django_login
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    InviteAcceptSerializer,
    UserSerializer,
)
from apps.accounts.exceptions import (
    DuplicateEmail,
    InvalidInviteToken,
    WeakPassword,
)
from apps.accounts.services import accept_invite

from ._errors import (
    DuplicateMemberError,
    InvalidInviteTokenError,
)


class InviteAcceptView(APIView):
    """Consume an invite + create the User + sign them in."""

    authentication_classes = (SessionAuth,)
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    @extend_schema(
        request=InviteAcceptSerializer,
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_invite_accept",
    )
    def post(self, request: Request) -> Response:
        serializer = InviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = accept_invite(
                uidb64=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                password=serializer.validated_data["password"],
            )
        except InvalidInviteToken as exc:
            raise InvalidInviteTokenError() from exc
        except DuplicateEmail as exc:
            raise DuplicateMemberError() from exc
        except WeakPassword as exc:
            raise ValidationError({"password": exc.messages}) from exc

        django_login(request, user)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )
