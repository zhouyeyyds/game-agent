from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
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
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    set_session_cookie(response, user.id)
    return to_user_response(user)


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return to_user_response(user)
