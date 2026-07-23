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
from app.schemas.auth import IDTokenRequest
from app.core.oauth import verify_google_id_token, verify_apple_id_token
from fastapi import HTTPException, status

def _get_or_create_user_oauth(session: Session, email: str, name: str, provider_id: str, provider: str) -> User:
    """Get or create a user via OAuth (Google or Apple)."""
    from app.models import User
    from app.repositories import UserRepository
    from app.core.security import hash_password
    import secrets

    user_repo = UserRepository(session)
    if provider == "google":
        user = user_repo.get_by_google_id(provider_id)
        if not user:
            # Try to find by email to link accounts
            user = user_repo.get_by_email(email)
            if user:
                # Link Google ID to existing account
                user.google_id = provider_id
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Create new user
                # Generate a unique phone number (10 digits)
                for _ in range(10):
                    phone = ''.join(str(secrets.randbelow(10)) for _ in range(10))
                    if not user_repo.get_by_phone(phone):
                        break
                else:
                    # Fallback: use a hash of email+timestamp (should be unique enough)
                    import hashlib
                    import time
                    hash_input = f"{email}{time.time()}".encode()
                    phone = hashlib.sha256(hash_input).hexdigest()[:10]
                user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    google_id=provider_id,
                    password_hash=hash_password(secrets.token_urlsafe(16)),
                    role="diner",
                    is_email_verified=True,
                )
                user = user_repo.add(user)
        return user
    elif provider == "apple":
        user = user_repo.get_by_apple_id(provider_id)
        if not user:
            user = user_repo.get_by_email(email)
            if user:
                user.apple_id = provider_id
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                for _ in range(10):
                    phone = ''.join(str(secrets.randbelow(10)) for _ in range(10))
                    if not user_repo.get_by_phone(phone):
                        break
                else:
                    import hashlib
                    import time
                    hash_input = f"{email}{time.time()}".encode()
                    phone = hashlib.sha256(hash_input).hexdigest()[:10]
                user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    apple_id=provider_id,
                    password_hash=hash_password(secrets.token_urlsafe(16)),
                    role="diner",
                    is_email_verified=True,
                )
                user = user_repo.add(user)
        return user
    else:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

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


@router.post("/auth/google")
async def google_auth(request: Request, body: IDTokenRequest, session: Session = Depends(get_session)):
    try:
        google_user_info = verify_google_id_token(body.id_token)
    except Exception as _:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token")
    email = google_user_info.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token missing email")
    name = google_user_info.get("name", "")
    google_id = google_user_info.get("sub")
    if not google_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token missing sub")
    user = _get_or_create_user_oauth(session, email, name, google_id, "google")
    token_pair = AuthService(session)._issue_token_pair(user)
    return token_pair


@router.post("/auth/apple")
async def apple_auth(request: Request, body: IDTokenRequest, session: Session = Depends(get_session)):
    try:
        apple_user_info = verify_apple_id_token(body.id_token)
    except Exception as _:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Apple ID token")
    email = apple_user_info.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple token missing email")
    name = apple_user_info.get("name", "")
    if isinstance(name, dict):
        first = name.get("firstName", "")
        last = name.get("lastName", "")
        name = f"{first} {last}".strip()
    apple_id = apple_user_info.get("sub")
    if not apple_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple token missing sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple token does not provide email")
    user = _get_or_create_user_oauth(session, email, name, apple_id, "apple")
    token_pair = AuthService(session)._issue_token_pair(user)
    return token_pair


# ── Legacy-compatible aliases (frontend/legacy-spa) ──────
router.add_api_route("/auth/signup", register, methods=["POST"], response_model=TokenPairResponse)
router.add_api_route("/auth/signin", login, methods=["POST"], response_model=TokenPairResponse)
router.add_api_route("/auth/signout", logout, methods=["POST"], response_model=MessageResponse)


@router.get("/users/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
