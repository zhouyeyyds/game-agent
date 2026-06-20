from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import TelemetryEvent, User
from app.schemas.telemetry import TelemetryEventRequest, TelemetryEventResponse

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

DbSession = Annotated[Session, Depends(get_db)]


def get_optional_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get(get_settings().jwt_cookie_name)
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None
    return db.get(User, user_id)


@router.post("/events", response_model=TelemetryEventResponse)
def create_telemetry_event(
    payload: TelemetryEventRequest,
    request: Request,
    db: DbSession,
) -> TelemetryEventResponse:
    user = get_optional_user(request, db)
    request_id = payload.requestId or getattr(request.state, "request_id", None)
    event = TelemetryEvent(
        request_id=request_id,
        user_id=user.id if user else None,
        event_type=payload.eventType,
        entity_type=payload.entityType,
        entity_id=payload.entityId,
        payload_json=payload.payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return TelemetryEventResponse(
        id=event.id,
        requestId=event.request_id,
        eventType=event.event_type,
        createdAt=event.created_at.isoformat(),
    )
