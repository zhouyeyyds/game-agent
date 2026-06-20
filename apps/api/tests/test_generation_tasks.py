from collections.abc import Iterator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.generation_tasks import cancel_task, list_tasks, retry_task
from app.core.constants import TaskStatus, TaskStep
from app.core.database import Base
from app.models import AgentLog, GenerationTask, User
from app.services import generation_pipeline


class InlineBackgroundTasks:
    def __init__(self) -> None:
        self.calls: list[tuple[object, tuple, dict]] = []

    def add_task(self, fn, *args, **kwargs) -> None:
        self.calls.append((fn, args, kwargs))


def make_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


def add_user(db: Session, email: str = "creator@example.com") -> User:
    user = User(email=email, password_hash="hash", display_name="Creator")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_task(
    db: Session,
    user: User,
    *,
    status: str = TaskStatus.PENDING,
    idea_text: str = "做一个太空跑酷游戏",
) -> GenerationTask:
    task = GenerationTask(
        user_id=user.id,
        status=str(status),
        idea_text=idea_text,
        input_assets_json=[],
        current_step=str(TaskStep.QUEUED),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_list_tasks_returns_only_current_user_tasks() -> None:
    db = next(make_session())
    user = add_user(db)
    other_user = add_user(db, "other@example.com")
    own_task = add_task(db, user)
    add_task(db, other_user)

    tasks = list_tasks(status_filter=None, user=user, db=db)

    assert [task.id for task in tasks] == [own_task.id]


def test_cancel_running_task_marks_canceled_and_logs() -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user, status=TaskStatus.RUNNING)

    response = cancel_task(task.id, user=user, db=db)

    assert response.status == TaskStatus.CANCELED
    assert response.finishedAt is not None
    assert db.scalar(select(AgentLog).where(AgentLog.task_id == task.id)) is not None


def test_retry_failed_task_creates_new_task_from_source() -> None:
    db = next(make_session())
    user = add_user(db)
    source = add_task(db, user, status=TaskStatus.FAILED, idea_text="重试这个创意")
    background_tasks = InlineBackgroundTasks()

    response = retry_task(source.id, background_tasks=background_tasks, user=user, db=db)

    assert response.id != source.id
    assert response.status == TaskStatus.PENDING
    assert response.ideaText == source.idea_text
    assert response.retriedFromTaskId == source.id
    assert len(background_tasks.calls) == 1


def test_pipeline_canceled_task_does_not_become_failed(monkeypatch) -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user, status=TaskStatus.CANCELED)

    def session_factory() -> Session:
        return db

    monkeypatch.setattr(generation_pipeline, "SessionLocal", session_factory, raising=False)

    assert generation_pipeline.should_skip_task(task) is True
