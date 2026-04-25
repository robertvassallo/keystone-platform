"""Custom DRF authentication classes.

The stock ``SessionAuthentication`` returns ``None`` from
``authenticate_header``, which causes DRF to rewrite 401 responses to 403
in ``APIView.handle_exception``. Our API contract returns **401** for
unauthenticated requests (see ``docs/01_architecture/api-conventions.md``);
this subclass restores that mapping by emitting a non-empty ``Session``
header.
"""

from __future__ import annotations

from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request


class SessionAuth(SessionAuthentication):
    """Session-cookie auth that returns proper 401s for anonymous requests."""

    def authenticate_header(self, request: Request) -> str:
        return "Session"
