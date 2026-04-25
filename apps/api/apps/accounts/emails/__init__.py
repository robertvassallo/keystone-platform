"""Public surface for outbound emails sent by the accounts app."""

from .send_password_reset_email import send_password_reset_email

__all__ = ["send_password_reset_email"]
