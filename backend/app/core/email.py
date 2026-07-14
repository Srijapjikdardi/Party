"""
Pluggable email delivery.

No SendGrid/SES/Mailgun — those cost money and are out of this
milestone's scope (see cost requirements: no third-party auth
providers, free-tier compatible). `LogEmailService` is the default:
it logs the email content (including the verification/reset link)
instead of sending it, which is enough to develop and test the full
token-issuance/verification flow end-to-end without paying for or
configuring an email provider.

To wire up real delivery later: implement `EmailService` with an SMTP
or provider-API backend and swap the instance `email_service` points
to below. Nothing else in the codebase needs to change — services call
`email_service.send_verification_email(...)` / `send_password_reset_email(...)`
without knowing which backend is behind it.
"""
import logging
from typing import Protocol

from app.core.config import settings

email_logger = logging.getLogger("partype.email")


class EmailService(Protocol):
    def send_verification_email(self, to_email: str, token: str) -> None: ...
    def send_password_reset_email(self, to_email: str, token: str) -> None: ...


class LogEmailService:
    def send_verification_email(self, to_email: str, token: str) -> None:
        link = f"{settings.public_app_url}/verify-email?token={token}"
        email_logger.info("EMAIL (verification) to=%s link=%s", to_email, link)

    def send_password_reset_email(self, to_email: str, token: str) -> None:
        link = f"{settings.public_app_url}/reset-password?token={token}"
        email_logger.info("EMAIL (password reset) to=%s link=%s", to_email, link)


email_service: EmailService = LogEmailService()
