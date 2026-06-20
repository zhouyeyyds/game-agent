from sqlalchemy import DateTime, inspect, text
from sqlalchemy.engine import Engine

from app.models import OAuthAccount


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("oauth_accounts"):
        OAuthAccount.__table__.create(bind=engine, checkfirst=True)

    if not inspector.has_table("generation_tasks"):
        return
    generation_task_columns = {column["name"] for column in inspector.get_columns("generation_tasks")}
    if "deleted_at" not in generation_task_columns:
        column_type = DateTime(timezone=True).compile(dialect=engine.dialect)
        with engine.begin() as connection:
            connection.execute(
                text(f"ALTER TABLE generation_tasks ADD COLUMN deleted_at {column_type} NULL")
            )
