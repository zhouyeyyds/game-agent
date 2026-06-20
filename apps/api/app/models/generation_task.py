from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    retried_from_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    idea_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_assets_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    current_step: Mapped[str] = mapped_column(String(120), default="queued")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_game_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    result_manifest_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    agent_step_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model_call_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    usage_json: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    logs = relationship("AgentLog", back_populates="task")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id: Mapped[str] = mapped_column(ForeignKey("generation_tasks.id"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(32), default="info")
    node_name: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task = relationship("GenerationTask", back_populates="logs")
