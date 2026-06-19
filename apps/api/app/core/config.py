from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"

    database_url: str = "mysql+pymysql://game_agent:game_agent_password@192.168.150.101:13306/game_agent"

    jwt_secret: str = "change-me-in-local-env"
    jwt_cookie_name: str = "game_agent_session"
    jwt_expire_minutes: int = 60 * 24 * 7

    minio_endpoint: str = "192.168.150.101:19000"
    minio_public_endpoint: str = "http://192.168.150.101:19000"
    minio_access_key: str = "game_agent_minio"
    minio_secret_key: str = "game_agent_minio_password"
    minio_bucket: str = "game-agent"
    minio_secure: bool = False

    llm_provider: str = Field(default="mock")


@lru_cache
def get_settings() -> Settings:
    return Settings()
