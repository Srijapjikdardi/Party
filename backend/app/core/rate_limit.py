"""
Rate limiting for auth endpoints (slowapi, in-memory backend).

In-memory: correct for a single-instance deployment (fine on a
free-tier single dyno/container) but each instance has its own
counters if scaled horizontally — documented limitation, not a bug.
Upgrading to a shared limit means pointing slowapi at Redis
(`storage_uri="redis://..."`), a one-line change here when that
infra exists; not added preemptively per the cost requirements.

`settings.rate_limit_enabled=False` (set in tests) makes every call a
no-op so test suites aren't rate-limited by shared state across cases.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, enabled=settings.rate_limit_enabled)

# Applied per-route via @limiter.limit(...). Kept as named constants so
# the actual numbers are visible in one place rather than scattered
# magic strings across endpoint files.
RATE_LIMIT_LOGIN = "5/minute"
RATE_LIMIT_REGISTER = "5/minute"
RATE_LIMIT_REFRESH = "20/minute"
RATE_LIMIT_FORGOT_PASSWORD = "3/minute"
RATE_LIMIT_RESET_PASSWORD = "5/minute"
RATE_LIMIT_RESEND_VERIFICATION = "3/minute"
