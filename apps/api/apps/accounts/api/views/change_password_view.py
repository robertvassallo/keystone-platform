"""View — POST /api/v1/auth/password/change/."""

from __future__ import annotations

from config.authentication import SessionAuth
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import ChangePasswordSerializer
from apps.accounts.exceptions import WeakPassword, WrongCurrentPassword
from apps.accounts.models import User
from apps.accounts.services import change_password

from ._audit import audit_context_from_request
from ._errors import WrongCurrentPasswordError


class ChangePasswordView(APIView):
    """Change the signed-in user's password.

    Keeps the current session live (auth hash is rotated); other sessions
    for this user are invalidated implicitly because Django ties session
    validity to the password hash.
    """

    authentication_classes = (SessionAuth,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: None,
        },
        operation_id="auth_password_change",
    )
    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        assert isinstance(user, User)

        try:
            change_password(
                request=request._request,
                user=user,
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["new_password"],
                audit_context=audit_context_from_request(request),
            )
        except WrongCurrentPassword as exc:
            raise WrongCurrentPasswordError() from exc
        except WeakPassword as exc:
            raise ValidationError({"new_password": exc.messages}) from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
