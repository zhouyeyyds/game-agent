from datetime import UTC, datetime

from app.agents.graph import build_generation_graph
from app.core.constants import AgentLogLevel, TaskStatus
from app.models import AgentLog, GenerationTask, User


def should_skip_task(task: GenerationTask) -> bool:
    if task.status == TaskStatus.SUCCEEDED and task.result_game_id:
        return True
    if task.status == TaskStatus.FAILED:
        return True
    if task.result_game_id:
        return True
    return False


def run_generation_pipeline(task_id: str, user_id: str) -> None:
    from app.core.database import SessionLocal

    with SessionLocal() as db:
        task = db.get(GenerationTask, task_id)
        user = db.get(User, user_id)
        if not task or not user or should_skip_task(task):
            return
        try:
            graph = build_generation_graph(db, task)
            graph.invoke(
                {
                    "task_id": task.id,
                    "user_id": user.id,
                    "idea_text": task.idea_text,
                    "asset_ids": task.input_assets_json or [],
                    "repair_attempts": 0,
                    "validation_errors": [],
                }
            )
        except Exception as exc:  # noqa: BLE001
            task.status = str(TaskStatus.FAILED)
            task.error_message = f"{type(exc).__name__}: {exc}"
            task.finished_at = datetime.now(UTC)
            db.add(
                AgentLog(
                    task_id=task.id,
                    level=str(AgentLogLevel.ERROR),
                    node_name=task.current_step,
                    message=task.error_message,
                )
            )
            db.commit()
