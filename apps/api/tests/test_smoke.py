"""Smoke tests — confirm the project loads its settings and core URLs resolve."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_returns_ok() -> None:
    """The /health/ endpoint returns a 200 with status=ok."""
    client = Client()
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_schema_endpoint_serves_openapi() -> None:
    """The /api/schema/ endpoint renders an OpenAPI document."""
    client = Client()
    response = client.get("/api/schema/")
    assert response.status_code == 200
