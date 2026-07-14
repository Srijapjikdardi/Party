"""
/api/v1/auth. See docs/AUTHENTICATION.md for the full flow.

Legacy compatibility: frontend/legacy-spa/index.html calls
/auth/signup, /auth/signin, /auth/signout (hitting these same handlers
via the unversioned /api alias — see app/main.py). Those three paths
are registered as aliases of /auth/register, /auth/login, /auth/logout
below so the legacy SPA keeps working unmodified.
"""
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.api.deps import get_client_ip, get_current_user
from app.core.rate_limit import (
    RATE_LIMIT_FORGOT_PASSWORD,
    RATE_LIMIT_LOGIN,
    RATE_LIMIT_REFRESH,
    RATE_LIMIT_REGISTER,
    RATE_LIMIT_RESEND_VERIFICATION,
    RATE_LIMIT_RESET_PASSWORD,
    limiter,
)
from app.db.session import get_session
from app.models import User
from app.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenPairResponse,
    UserRead,
    VerifyEmailRequest,
)
from app.services import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenPairResponse)
@limiter.limit(RATE_LIMIT_REGISTER)
def register(request: Request, user_data: RegisterRequest, session: Session = Depends(get_session)):
    tokens, _ = AuthService(session).register(user_data, ip=get_client_ip(request))
    return tokens


@router.post("/auth/login", response_model=TokenPairResponse)
@limiter.limit(RATE_LIMIT_LOGIN)
def login(request: Request, creds: LoginRequest, session: Session = Depends(get_session)):
    tokens, _ = AuthService(session).login(creds, ip=get_client_ip(request))
    return tokens


@router.post("/auth/logout", response_model=MessageResponse)
def logout(request: Request, body: LogoutRequest, session: Session = Depends(get_session)):
    AuthService(session).logout(body.refresh_token, ip=get_client_ip(request))
    return MessageResponse(message="Signed out")


@router.post("/auth/refresh", response_model=TokenPairResponse)
@limiter.limit(RATE_LIMIT_REFRESH)
def refresh(request: Request, body: RefreshRequest, session: Session = Depends(get_session)):
    return AuthService(session).refresh(body.refresh_token, ip=get_client_ip(request))


@router.post("/auth/verify-email", response_model=MessageResponse)
def verify_email(body: VerifyEmailRequest, session: Session = Depends(get_session)):
    AuthService(session).verify_email(body.token)
    return MessageResponse(message="Email verified")


@router.post("/auth/resend-verification", response_model=MessageResponse)
@limiter.limit(RATE_LIMIT_RESEND_VERIFICATION)
def resend_verification(
    request: Request, body: ResendVerificationRequest, session: Session = Depends(get_session)
):
    AuthService(session).resend_verification(body.email)
    return MessageResponse(message="If that email is registered and unverified, a new link has been sent")


@router.post("/auth/forgot-password", response_model=MessageResponse)
@limiter.limit(RATE_LIMIT_FORGOT_PASSWORD)
def forgot_password(request: Request, body: ForgotPasswordRequest, session: Session = Depends(get_session)):
    AuthService(session).forgot_password(body.email, ip=get_client_ip(request))
    return MessageResponse(message="If that email is registered, a reset link has been sent")


@router.post("/auth/reset-password", response_model=MessageResponse)
@limiter.limit(RATE_LIMIT_RESET_PASSWORD)
def reset_password(request: Request, body: ResetPasswordRequest, session: Session = Depends(get_session)):
    AuthService(session).reset_password(body.token, body.new_password, ip=get_client_ip(request))
    return MessageResponse(message="Password has been reset")


# ── Legacy-compatible aliases (frontend/legacy-spa) ──────
router.add_api_route("/auth/signup", register, methods=["POST"], response_model=TokenPairResponse)
router.add_api_route("/auth/signin", login, methods=["POST"], response_model=TokenPairResponse)
router.add_api_route("/auth/signout", logout, methods=["POST"], response_model=MessageResponse)


@router.get("/users/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
