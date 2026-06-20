from sqlalchemy import DateTime, Float, Integer, JSON, inspect, text
from sqlalchemy.engine import Engine

from app.models import OAuthAccount, TelemetryEvent


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("oauth_accounts"):
        OAuthAccount.__table__.create(bind=engine, checkfirst=True)
    if not inspector.has_table("telemetry_events"):
        TelemetryEvent.__table__.create(bind=engine, checkfirst=True)

    if not inspector.has_table("generation_tasks"):
        return
    generation_task_columns = {column["name"] for column in inspector.get_columns("generation_tasks")}
    if "deleted_at" not in generation_task_columns:
        column_type = DateTime(timezone=True).compile(dialect=engine.dialect)
        with engine.begin() as connection:
            connection.execute(
                text(f"ALTER TABLE generation_tasks ADD COLUMN deleted_at {column_type} NULL")
            )

    metric_columns = {
        "agent_step_count": f"{Integer().compile(dialect=engine.dialect)} NOT NULL DEFAULT 0",
        "model_call_count": f"{Integer().compile(dialect=engine.dialect)} NOT NULL DEFAULT 0",
        "prompt_tokens": f"{Integer().compile(dialect=engine.dialect)} NOT NULL DEFAULT 0",
        "completion_tokens": f"{Integer().compile(dialect=engine.dialect)} NOT NULL DEFAULT 0",
        "total_tokens": f"{Integer().compile(dialect=engine.dialect)} NOT NULL DEFAULT 0",
        "estimated_cost_usd": f"{Float().compile(dialect=engine.dialect)} NULL",
        "usage_json": f"{JSON().compile(dialect=engine.dialect)} NULL",
    }
    with engine.begin() as connection:
        for column_name, column_type in metric_columns.items():
            if column_name not in generation_task_columns:
                connection.execute(
                    text(f"ALTER TABLE generation_tasks ADD COLUMN {column_name} {column_type}")
                )
                generation_task_columns.add(column_name)
