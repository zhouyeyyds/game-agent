from pydantic import BaseModel, Field


class TelemetryEventRequest(BaseModel):
    eventType: str = Field(min_length=1, max_length=120)
    entityType: str | None = Field(default=None, max_length=80)
    entityId: str | None = Field(default=None, max_length=128)
    requestId: str | None = Field(default=None, max_length=128)
    payload: dict | None = None


class TelemetryEventResponse(BaseModel):
    id: str
    requestId: str | None = None
    eventType: str
    createdAt: str
