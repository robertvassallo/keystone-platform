"""Django AppConfig for the accounts app."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Domain app for user accounts and authentication."""

    name = "apps.accounts"
    label = "accounts"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Accounts"
