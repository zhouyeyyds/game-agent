from collections.abc import Iterator
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.llm import _read_usage
from app.agents.nodes import record_llm_usage
from app.api.routes.generation_tasks import to_task_response
from app.core.config import get_settings
from app.core.database import Base, get_db
from app.db.schema_upgrade import ensure_runtime_schema
from app.main import create_app
from app.models import GenerationTask, TelemetryEvent, User


def make_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


def add_user(db: Session) -> User:
    user = User(email="creator@example.com", password_hash="hash", display_name="Creator")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_task(db: Session, user: User) -> GenerationTask:
    task = GenerationTask(
        user_id=user.id,
        status="running",
        idea_text="make a game",
        input_assets_json=[],
        current_step="code_generation",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def make_client(db: Session) -> TestClient:
    app = create_app()

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_request_id_middleware_generates_and_echoes_header() -> None:
    db = next(make_session())
    client = make_client(db)

    generated = client.get("/api/health")
    echoed = client.get("/api/health", headers={"X-Request-ID": "req-test-1"})

    assert generated.headers["X-Request-ID"]
    assert echoed.headers["X-Request-ID"] == "req-test-1"


def test_telemetry_event_accepts_anonymous_event() -> None:
    db = next(make_session())
    client = make_client(db)

    response = client.post(
        "/api/telemetry/events",
        json={
            "eventType": "manifest_fetch_success",
            "entityType": "game",
            "entityId": "game-1",
            "payload": {"elapsedMs": 42},
        },
        headers={"X-Request-ID": "req-telemetry"},
    )

    assert response.status_code == 200
    event = db.scalar(select(TelemetryEvent))
    assert event is not None
    assert event.request_id == "req-telemetry"
    assert event.user_id is None
    assert event.payload_json == {"elapsedMs": 42}


def test_task_metrics_response_uses_zero_safe_defaults() -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user)

    response = to_task_response(task)

    assert response.metrics.agentStepCount == 0
    assert response.metrics.modelCallCount == 0
    assert response.metrics.totalTokens == 0
    assert response.metrics.estimatedCostUsd is None


def test_llm_usage_aggregation_records_tokens_and_cost(monkeypatch) -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user)
    settings = get_settings()
    monkeypatch.setattr(settings, "llm_input_cost_per_1m_tokens", 2.0)
    monkeypatch.setattr(settings, "llm_output_cost_per_1m_tokens", 8.0)

    result = SimpleNamespace(
        model="gpt-test",
        elapsed_ms=123,
        usage=_read_usage(
            SimpleNamespace(
                usage=SimpleNamespace(
                    prompt_tokens=1000,
                    completion_tokens=500,
                    total_tokens=1500,
                )
            )
        ),
    )

    usage_entry = record_llm_usage(db, task, "code_generation_agent", result)  # type: ignore[arg-type]

    db.refresh(task)
    assert task.model_call_count == 1
    assert task.prompt_tokens == 1000
    assert task.completion_tokens == 500
    assert task.total_tokens == 1500
    assert task.estimated_cost_usd == 0.006
    assert usage_entry["estimatedCostUsd"] == 0.006
    assert task.usage_json and task.usage_json[0]["model"] == "gpt-test"
