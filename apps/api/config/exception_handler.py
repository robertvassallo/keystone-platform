"""DRF exception handler emitting RFC 7807 problem-details responses.

Spec: https://www.rfc-editor.org/rfc/rfc7807. Shape mirrors
``docs/01_architecture/api-conventions.md``.

The ``type`` URI is intentionally ``about:blank#<code>`` for now — once a
public errors documentation site exists, swap that prefix for the
documented base URL without changing the rest of the contract.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

PROBLEM_TYPE_PREFIX = "about:blank#"


def problem_details_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    """Wrap the default DRF handler and reshape its output to RFC 7807.

    Returns ``None`` for exceptions DRF declines to handle — those bubble up
    to Django's default 500 page (production never exposes them; the prod
    settings file enforces ``DEBUG=False``).
    """
    response = drf_default_handler(exc, context)
    if response is None:
        return None

    request = context.get("request")
    request_id = ""
    instance = ""
    if request is not None:
        request_id = request.META.get("HTTP_X_REQUEST_ID", "")
        instance = request.path

    code, title, detail = _classify(exc, response)

    body: dict[str, Any] = {
        "type": f"{PROBLEM_TYPE_PREFIX}{code}",
        "title": title,
        "status": response.status_code,
        "detail": detail,
        "instance": instance,
        "request_id": request_id,
    }

    # Validation failures include per-field errors. DRF gives us a
    # dict of field → list[str]; pass it through unchanged.
    if response.status_code == status.HTTP_400_BAD_REQUEST and isinstance(
        response.data, dict
    ):
        body["errors"] = response.data

    response.data = body
    return response


def _classify(exc: Exception, response: Response) -> tuple[str, str, str]:
    """Derive (code, title, detail) from a DRF exception."""
    if isinstance(exc, APIException):
        code = exc.default_code or type(exc).__name__.lower()
        title = type(exc).__name__
        detail = _stringify_detail(exc.detail)
    else:
        code = type(exc).__name__.lower()
        title = type(exc).__name__
        detail = str(exc) or title
    return (code, title, detail)


def _stringify_detail(detail: Any) -> str:
    """Reduce DRF's nested ``detail`` types to a single human-readable string."""
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return _stringify_detail(detail[0])
    if isinstance(detail, dict) and detail:
        first_value = next(iter(detail.values()))
        return _stringify_detail(first_value)
    return str(detail)
