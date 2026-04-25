"""Root URL configuration.

Mounts the versioned API under ``/api/v1/``, the OpenAPI schema at
``/api/schema/``, Swagger UI at ``/api/docs/``, the Django admin at
``/admin/``, and a liveness endpoint at ``/health/``.
"""

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request: HttpRequest) -> JsonResponse:
    """Return a static OK payload — used by load balancers and dev probes."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("api/v1/", include(("config.api_v1_urls", "api_v1"), namespace="api_v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
