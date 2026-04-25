"""Re-exports the accounts api URL module so ``include('apps.accounts.urls')`` works."""

from apps.accounts.api.urls import app_name, urlpatterns

__all__ = ["app_name", "urlpatterns"]
