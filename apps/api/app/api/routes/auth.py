from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import Annotated, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import ALGORITHM, create_access_token, hash_password, verify_password
from app.models import OAuthAccount, User
from app.schemas.auth import (
    LoginRequest,
    OAuthProvidersResponse,
    OAuthProviderStatus,
    RegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"
OAUTH_STATE_COOKIE = "game_agent_oauth_state"
OAUTH_STATE_EXPIRE_MINUTES = 10
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def to_user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, displayName=user.display_name)


def set_session_cookie(response: Response, user_id: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.jwt_cookie_name,
        value=create_access_token(user_id),
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=settings.jwt_cookie_name,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
        path="/",
    )


def set_oauth_state_cookie(response: Response, state_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state_token,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
        max_age=OAUTH_STATE_EXPIRE_MINUTES * 60,
        path="/",
    )


def clear_oauth_state_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=OAUTH_STATE_COOKIE,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
        path="/",
    )


def is_github_oauth_configured() -> bool:
    settings = get_settings()
    return bool(settings.github_oauth_client_id and settings.github_oauth_client_secret)


def sanitize_redirect_path(value: str | None) -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/create"
    if "://" in value or "\\" in value:
        return "/create"
    return value


def frontend_redirect_url(path: str, error: str | None = None) -> str:
    settings = get_settings()
    safe_path = sanitize_redirect_path(path)
    if not error:
        return f"{settings.frontend_origin}{safe_path}"
    separator = "&" if "?" in safe_path else "?"
    return f"{settings.frontend_origin}{safe_path}{separator}{urlencode({'oauth_error': error})}"


def create_oauth_state(provider: str, redirect_path: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES)
    return jwt.encode(
        {
            "provider": provider,
            "redirect": sanitize_redirect_path(redirect_path),
            "exp": expires_at,
        },
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )


def decode_oauth_state(state_token: str) -> dict[str, str]:
    settings = get_settings()
    try:
        payload = jwt.decode(state_token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        ) from exc
    provider = payload.get("provider")
    redirect_path = payload.get("redirect")
    if not isinstance(provider, str) or not isinstance(redirect_path, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
    return {"provider": provider, "redirect": sanitize_redirect_path(redirect_path)}


def verify_oauth_state(request: Request, state: str) -> dict[str, str]:
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not cookie_state or state != cookie_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state mismatch")
    return decode_oauth_state(state)


def fetch_github_identity(code: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.github_oauth_client_id or not settings.github_oauth_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )

    try:
        with httpx.Client(timeout=15.0) as client:
            token_response = client.post(
                GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.github_oauth_client_id,
                    "client_secret": settings.github_oauth_client_secret,
                    "code": code,
                    "redirect_uri": settings.github_oauth_callback_url,
                },
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            access_token = token_payload.get("access_token")
            if not isinstance(access_token, str) or not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub token exchange failed",
                )

            auth_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            user_response = client.get(GITHUB_USER_URL, headers=auth_headers)
            user_response.raise_for_status()
            emails_response = client.get(GITHUB_EMAILS_URL, headers=auth_headers)
            emails_response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub OAuth request failed",
        ) from exc

    github_user = user_response.json()
    github_emails = emails_response.json()
    if not isinstance(github_user, dict) or not isinstance(github_emails, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid GitHub OAuth response",
        )

    verified_email = next(
        (
            item.get("email")
            for item in github_emails
            if (
                isinstance(item, dict)
                and item.get("primary") is True
                and item.get("verified") is True
            )
        ),
        None,
    )
    if not isinstance(verified_email, str) or not verified_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub account has no verified primary email",
        )

    github_id = github_user.get("id")
    if github_id is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub profile is missing id",
        )

    github_login = github_user.get("login")
    github_avatar_url = github_user.get("avatar_url")
    github_name = github_user.get("name")

    return {
        "provider_account_id": str(github_id),
        "email": verified_email,
        "username": github_login if isinstance(github_login, str) else None,
        "avatar_url": github_avatar_url if isinstance(github_avatar_url, str) else None,
        "display_name": github_name if isinstance(github_name, str) else None,
    }


def get_or_create_github_user(db: Session, identity: dict[str, Any]) -> User:
    oauth_account = db.scalar(
        select(OAuthAccount).where(
            OAuthAccount.provider == "github",
            OAuthAccount.provider_account_id == identity["provider_account_id"],
        )
    )
    if oauth_account:
        oauth_account.provider_email = identity["email"]
        oauth_account.provider_username = identity["username"]
        oauth_account.avatar_url = identity["avatar_url"]
        user = db.get(User, oauth_account.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OAuth user not found",
            )
        if identity["avatar_url"] and not user.avatar_url:
            user.avatar_url = identity["avatar_url"]
        db.commit()
        db.refresh(user)
        return user

    user = db.scalar(select(User).where(User.email == identity["email"]))
    if not user:
        display_name = (
            identity["display_name"]
            or identity["username"]
            or identity["email"].split("@")[0]
        )
        user = User(
            email=identity["email"],
            password_hash=hash_password(token_urlsafe(32)),
            display_name=display_name[:120],
            avatar_url=identity["avatar_url"],
        )
        db.add(user)
        db.flush()

    account = OAuthAccount(
        user_id=user.id,
        provider="github",
        provider_account_id=identity["provider_account_id"],
        provider_email=identity["email"],
        provider_username=identity["username"],
        avatar_url=identity["avatar_url"],
    )
    db.add(account)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=UserResponse)
def register(
    payload: RegisterRequest,
    response: Response,
    db: DbSession,
) -> UserResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        display_name=payload.displayName,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    set_session_cookie(response, user.id)
    return to_user_response(user)


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: DbSession) -> UserResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    set_session_cookie(response, user.id)
    return to_user_response(user)


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> UserResponse:
    return to_user_response(user)


@router.get("/oauth/providers", response_model=OAuthProvidersResponse)
def oauth_providers() -> OAuthProvidersResponse:
    github_configured = is_github_oauth_configured()
    return OAuthProvidersResponse(
        providers=[
            OAuthProviderStatus(
                provider="github",
                configured=github_configured,
                status="configured" if github_configured else "missing_config",
                startUrl="/api/auth/oauth/github/start" if github_configured else None,
            ),
            OAuthProviderStatus(
                provider="google",
                configured=False,
                status="planned",
                startUrl="/api/auth/oauth/google/start",
            ),
        ]
    )


@router.get("/oauth/github/start")
def github_oauth_start(
    redirect: str = Query(default="/create"),
) -> RedirectResponse:
    settings = get_settings()
    if not settings.github_oauth_client_id or not settings.github_oauth_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )

    safe_redirect = sanitize_redirect_path(redirect)
    state_token = create_oauth_state("github", safe_redirect)
    params = urlencode(
        {
            "client_id": settings.github_oauth_client_id,
            "redirect_uri": settings.github_oauth_callback_url,
            "scope": "read:user user:email",
            "state": state_token,
        }
    )
    response = RedirectResponse(
        f"{GITHUB_AUTHORIZE_URL}?{params}",
        status_code=status.HTTP_302_FOUND,
    )
    set_oauth_state_cookie(response, state_token)
    return response


@router.get("/oauth/github/callback")
def github_oauth_callback(
    request: Request,
    response: Response,
    db: DbSession,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    redirect_path = "/create"
    redirect_response: RedirectResponse
    try:
        if error:
            redirect_response = RedirectResponse(frontend_redirect_url("/login", f"github_{error}"))
            clear_oauth_state_cookie(redirect_response)
            return redirect_response
        if not code or not state:
            redirect_response = RedirectResponse(
                frontend_redirect_url("/login", "github_missing_code")
            )
            clear_oauth_state_cookie(redirect_response)
            return redirect_response

        state_payload = verify_oauth_state(request, state)
        if state_payload["provider"] != "github":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth provider",
            )
        redirect_path = state_payload["redirect"]
        identity = fetch_github_identity(code)
        user = get_or_create_github_user(db, identity)
        redirect_response = RedirectResponse(
            frontend_redirect_url(redirect_path),
            status_code=status.HTTP_302_FOUND,
        )
        set_session_cookie(redirect_response, user.id)
        clear_oauth_state_cookie(redirect_response)
        return redirect_response
    except HTTPException as exc:
        redirect_response = RedirectResponse(frontend_redirect_url("/login", str(exc.detail)))
        clear_oauth_state_cookie(redirect_response)
        return redirect_response


@router.get("/oauth/google/start")
def google_oauth_start() -> RedirectResponse:
    return RedirectResponse(
        frontend_redirect_url("/login", "google_not_configured"),
        status_code=status.HTTP_302_FOUND,
    )
