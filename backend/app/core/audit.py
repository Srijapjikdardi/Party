"""
Audit logging for authentication events.

Structured logging, not a database table: auth events (login attempts,
registrations, password resets, etc.) are high-frequency and not on
any read path the app itself needs — writing them to Postgres would
add write load and storage cost for data whose only consumer is a
human or log-aggregation tool after the fact. Any free-tier host
(Render, Railway, Fly.io, etc.) captures stdout/stderr automatically,
so this needs no additional infrastructure. If a queryable audit trail
becomes a real product requirement later, promote this to a table then
— not preemptively.
"""
import logging
from typing import Optional
from uuid import UUID

audit_logger = logging.getLogger("partype.audit")


def log_auth_event(
    event: str,
    *,
    success: bool,
    user_id: Optional[UUID] = None,
    email: Optional[str] = None,
    ip: Optional[str] = None,
    detail: str = "",
) -> None:
    """
    `event` is one of: register, login, logout, refresh, refresh_reuse_detected,
    change_password, deactivate, delete_account, verify_email,
    resend_verification, forgot_password, reset_password.
    """
    audit_logger.info(
        "event=%s success=%s user_id=%s email=%s ip=%s detail=%s",
        event, success, user_id, email, ip, detail,
    )
