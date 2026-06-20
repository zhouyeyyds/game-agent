from datetime import UTC, datetime

from app.agents.graph import build_generation_graph
from app.agents.nodes import GenerationCanceled
from app.core.constants import AgentLogLevel, TaskStatus
from app.models import AgentLog, GenerationTask, User


def should_skip_task(task: GenerationTask) -> bool:
    terminal_statuses = {
        str(TaskStatus.SUCCEEDED),
        str(TaskStatus.FAILED),
        str(TaskStatus.CANCELED),
    }
    if task.status in terminal_statuses:
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
                    "security_errors": [],
                }
            )
        except GenerationCanceled:
            task.status = str(TaskStatus.CANCELED)
            if not task.error_message:
                task.error_message = "Generation task was canceled by the creator."
            if not task.finished_at:
                task.finished_at = datetime.now(UTC)
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.refresh(task)
            if task.status == str(TaskStatus.CANCELED):
                if not task.finished_at:
                    task.finished_at = datetime.now(UTC)
                db.commit()
                return
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
