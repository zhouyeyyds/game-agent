from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
