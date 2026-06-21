from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator
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

    vm_host: str = "192.168.150.101"

    mysql_host: str = ""
    mysql_port: int = 13306
    mysql_database: str = "game_agent"
    mysql_user: str = "game_agent"
    mysql_password: str = "game_agent_password"
    database_url: str = ""

    jwt_secret: str = "change-me-in-local-env"
    jwt_cookie_name: str = "game_agent_session"
    jwt_expire_minutes: int = 60 * 24 * 7

    github_oauth_client_id: str | None = None
    github_oauth_client_secret: str | None = None
    github_oauth_callback_url: str = "http://localhost:18000/api/auth/oauth/github/callback"

    minio_endpoint: str = ""
    minio_public_endpoint: str = ""
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

    @model_validator(mode="after")
    def apply_vm_host_defaults(self) -> Self:
        mysql_host = self._default_to_vm_host(self.mysql_host)
        self.mysql_host = mysql_host

        if not self.database_url:
            self.database_url = (
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
                f"@{mysql_host}:{self.mysql_port}/{self.mysql_database}"
            )

        if not self.minio_endpoint:
            self.minio_endpoint = f"{self.vm_host}:19000"

        if not self.minio_public_endpoint:
            self.minio_public_endpoint = f"http://{self.minio_endpoint}"

        return self

    def _default_to_vm_host(self, value: str) -> str:
        normalized = value.strip()
        if normalized in {"", "$VM_HOST", "${VM_HOST}"}:
            return self.vm_host
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
