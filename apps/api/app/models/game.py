from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    current_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="games")
    versions = relationship("GameVersion", back_populates="game")


class GameVersion(Base):
    __tablename__ = "game_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), nullable=False)
    generation_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    game_spec_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    manifest_url: Mapped[str] = mapped_column(String(512), nullable=False)
    bundle_url: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_prefix: Mapped[str] = mapped_column(String(512), nullable=False)
    runtime_type: Mapped[str] = mapped_column(String(64), default="iframe_manifest_v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    game = relationship("Game", back_populates="versions")
