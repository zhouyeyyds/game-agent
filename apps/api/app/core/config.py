from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", API_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"

    database_url: str = "mysql+pymysql://game_agent:game_agent_password@192.168.150.101:13306/game_agent"

    jwt_secret: str = "change-me-in-local-env"
    jwt_cookie_name: str = "game_agent_session"
    jwt_expire_minutes: int = 60 * 24 * 7

    github_oauth_client_id: str | None = None
    github_oauth_client_secret: str | None = None
    github_oauth_callback_url: str = "http://localhost:18000/api/auth/oauth/github/callback"

    minio_endpoint: str = "192.168.150.101:19000"
    minio_public_endpoint: str = "http://192.168.150.101:19000"
    minio_access_key: str = "game_agent_minio"
    minio_secret_key: str = "game_agent_minio_password"
    minio_bucket: str = "game-agent"
    minio_secure: bool = False

    llm_provider: str = Field(default="openai_compatible")
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"
    llm_temperature: float = 0.4
    llm_timeout_seconds: int = 300
    llm_max_retries: int = 2
    llm_input_cost_per_1m_tokens: float = 0.0
    llm_output_cost_per_1m_tokens: float = 0.0
    agent_max_repair_attempts: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
