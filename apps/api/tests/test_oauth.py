from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import auth
from app.api.routes.auth import (
    create_oauth_state,
    get_or_create_github_user,
    github_oauth_start,
    oauth_providers,
    verify_oauth_state,
)
from app.core.database import Base
from app.models import OAuthAccount, User


class FakeRequest:
    def __init__(self, cookies: dict[str, str]) -> None:
        self.cookies = cookies


def make_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


def add_user(db: Session, email: str = "creator@example.com") -> User:
    user = User(email=email, password_hash="hash", display_name="Creator")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_oauth_providers_reflect_github_configuration(monkeypatch) -> None:
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_id", None)
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_secret", None)

    response = oauth_providers()

    github = next(provider for provider in response.providers if provider.provider == "github")
    google = next(provider for provider in response.providers if provider.provider == "google")
    assert github.configured is False
    assert github.status == "missing_config"
    assert google.configured is False
    assert google.status == "planned"

    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_id", "client")
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_secret", "secret")

    response = oauth_providers()

    github = next(provider for provider in response.providers if provider.provider == "github")
    assert github.configured is True
    assert github.startUrl == "/api/auth/oauth/github/start"


def test_github_start_requires_config(monkeypatch) -> None:
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_id", None)
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_secret", None)

    with pytest.raises(Exception) as caught:
        github_oauth_start()

    assert getattr(caught.value, "status_code", None) == 503


def test_github_start_redirects_and_sets_state_cookie(monkeypatch) -> None:
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_id", "client-id")
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_secret", "secret")
    monkeypatch.setattr(
        auth.get_settings(),
        "github_oauth_callback_url",
        "http://localhost:18000/api/auth/oauth/github/callback",
    )

    response = github_oauth_start(redirect="/create")

    assert response.status_code == 302
    assert str(response.headers["location"]).startswith("https://github.com/login/oauth/authorize?")
    assert "client_id=client-id" in response.headers["location"]
    assert "game_agent_oauth_state=" in response.headers["set-cookie"]


def test_verify_oauth_state_rejects_missing_or_mismatch() -> None:
    state = create_oauth_state("github", "/create")

    with pytest.raises(Exception) as caught:
        verify_oauth_state(FakeRequest(cookies={}), state)  # type: ignore[arg-type]
    assert getattr(caught.value, "status_code", None) == 400

    with pytest.raises(Exception) as caught:
        verify_oauth_state(FakeRequest(cookies={auth.OAUTH_STATE_COOKIE: "other"}), state)  # type: ignore[arg-type]
    assert getattr(caught.value, "status_code", None) == 400


def test_github_identity_binds_existing_verified_email_user() -> None:
    db = next(make_session())
    user = add_user(db, "creator@example.com")

    result = get_or_create_github_user(
        db,
        {
            "provider_account_id": "1001",
            "email": "creator@example.com",
            "username": "creator",
            "avatar_url": "https://avatars.example.com/u/1001",
            "display_name": "Creator Name",
        },
    )

    assert result.id == user.id
    account = db.scalar(select(OAuthAccount).where(OAuthAccount.provider_account_id == "1001"))
    assert account is not None
    assert account.user_id == user.id


def test_github_identity_creates_user_without_existing_email() -> None:
    db = next(make_session())

    user = get_or_create_github_user(
        db,
        {
            "provider_account_id": "1002",
            "email": "new@example.com",
            "username": "newbie",
            "avatar_url": "https://avatars.example.com/u/1002",
            "display_name": None,
        },
    )

    assert user.email == "new@example.com"
    assert user.display_name == "newbie"
    assert db.scalar(select(OAuthAccount).where(OAuthAccount.user_id == user.id)) is not None


def test_github_identity_reuses_existing_oauth_account() -> None:
    db = next(make_session())
    first = get_or_create_github_user(
        db,
        {
            "provider_account_id": "1003",
            "email": "same@example.com",
            "username": "same",
            "avatar_url": None,
            "display_name": "Same",
        },
    )

    second = get_or_create_github_user(
        db,
        {
            "provider_account_id": "1003",
            "email": "updated@example.com",
            "username": "same-updated",
            "avatar_url": None,
            "display_name": "Updated",
        },
    )

    assert second.id == first.id
    assert len(db.scalars(select(User)).all()) == 1
    assert len(db.scalars(select(OAuthAccount)).all()) == 1


def test_fetch_github_identity_rejects_missing_verified_email(monkeypatch) -> None:
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self.payload

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, *args, **kwargs):
            return FakeResponse({"access_token": "token"})

        def get(self, url, *args, **kwargs):
            if url == auth.GITHUB_USER_URL:
                return FakeResponse({"id": 1, "login": "octo"})
            return FakeResponse([{"email": "octo@example.com", "primary": True, "verified": False}])

    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_id", "client")
    monkeypatch.setattr(auth.get_settings(), "github_oauth_client_secret", "secret")
    monkeypatch.setattr(auth.httpx, "Client", FakeClient)

    with pytest.raises(Exception) as caught:
        auth.fetch_github_identity("code")

    assert getattr(caught.value, "status_code", None) == 400
