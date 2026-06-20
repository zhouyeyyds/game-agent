from collections.abc import Iterator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.games import get_play_descriptor, list_games, unpublish_game, update_game
from app.api.routes.generation_tasks import (
    delete_task,
    get_task,
    list_tasks,
    cancel_task,
    publish_task,
    retry_task,
)
from app.core.constants import GameStatus, TaskStatus, TaskStep
from app.core.database import Base
from app.models import AgentLog, Game, GameVersion, GenerationTask, User
from app.schemas.game import UpdateGameRequest
from app.schemas.task import PublishTaskRequest
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


def add_publishable_task(db: Session, user: User) -> tuple[GenerationTask, Game]:
    task = add_task(db, user, status=TaskStatus.SUCCEEDED)
    game = Game(
        owner_user_id=user.id,
        title="草稿标题",
        description="草稿描述",
        cover_url=None,
        status=str(GameStatus.DRAFT),
        tags=["草稿"],
    )
    db.add(game)
    db.flush()
    version = GameVersion(
        game_id=game.id,
        generation_task_id=task.id,
        version_number=1,
        game_spec_json=None,
        manifest_url="https://cdn.example.com/manifest.json",
        bundle_url="https://cdn.example.com/bundle.zip",
        storage_prefix="games/demo",
    )
    db.add(version)
    db.flush()
    game.current_version_id = version.id
    task.result_game_id = game.id
    task.result_manifest_url = version.manifest_url
    db.commit()
    db.refresh(task)
    db.refresh(game)
    return task, game


def test_list_tasks_returns_only_current_user_tasks() -> None:
    db = next(make_session())
    user = add_user(db)
    other_user = add_user(db, "other@example.com")
    own_task = add_task(db, user)
    add_task(db, other_user)

    tasks = list_tasks(status_filter=None, user=user, db=db)

    assert [task.id for task in tasks] == [own_task.id]


def test_delete_terminal_task_hides_it_from_history_and_detail() -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user, status=TaskStatus.FAILED)

    response = delete_task(task.id, user=user, db=db)

    db.refresh(task)
    assert response.status_code == 204
    assert task.deleted_at is not None
    assert list_tasks(status_filter=None, user=user, db=db) == []
    try:
        get_task(task.id, user=user, db=db)
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 404
    else:
        raise AssertionError("Expected deleted task detail to be hidden")


def test_delete_task_rejects_non_owner_and_active_task() -> None:
    db = next(make_session())
    user = add_user(db)
    other_user = add_user(db, "other-delete@example.com")
    active_task = add_task(db, user, status=TaskStatus.RUNNING)
    done_task = add_task(db, user, status=TaskStatus.SUCCEEDED)

    try:
        delete_task(done_task.id, user=other_user, db=db)
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 404
    else:
        raise AssertionError("Expected non-owner delete to be rejected")

    try:
        delete_task(active_task.id, user=user, db=db)
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 400
    else:
        raise AssertionError("Expected active task delete to be rejected")


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


def test_publish_task_saves_game_metadata_and_sets_published_at() -> None:
    db = next(make_session())
    user = add_user(db)
    task, game = add_publishable_task(db, user)

    response = publish_task(
        task.id,
        payload=PublishTaskRequest(
            title="正式标题",
            description="正式描述",
            coverUrl="https://cdn.example.com/cover.png",
            tags=["冒险", "解谜"],
        ),
        user=user,
        db=db,
    )

    db.refresh(game)
    assert game.status == GameStatus.PUBLISHED
    assert game.published_at is not None
    assert game.title == "正式标题"
    assert game.description == "正式描述"
    assert game.cover_url == "https://cdn.example.com/cover.png"
    assert game.tags == ["冒险", "解谜"]
    assert response.result.publishedAt is not None
    assert response.result.title == "正式标题"
    assert response.result.tags == ["冒险", "解谜"]
    assert response.result.gameStatus == str(GameStatus.PUBLISHED)


def test_update_published_game_metadata_keeps_published_at() -> None:
    db = next(make_session())
    user = add_user(db)
    task, game = add_publishable_task(db, user)
    publish_task(
        task.id,
        payload=PublishTaskRequest(title="正式标题", description="正式描述", tags=["冒险"]),
        user=user,
        db=db,
    )
    db.refresh(game)
    published_at = game.published_at

    response = update_game(
        game.id,
        payload=UpdateGameRequest(
            title="更新标题",
            description="更新描述",
            coverUrl="https://cdn.example.com/new-cover.png",
            tags=["策略"],
        ),
        user=user,
        db=db,
    )

    db.refresh(game)
    assert game.published_at == published_at
    assert response.title == "更新标题"
    assert response.coverUrl == "https://cdn.example.com/new-cover.png"
    assert response.tags == ["策略"]


def test_delete_published_task_does_not_change_game_status() -> None:
    db = next(make_session())
    user = add_user(db)
    task, game = add_publishable_task(db, user)
    publish_task(
        task.id,
        payload=PublishTaskRequest(title="正式标题", description="正式描述", tags=[]),
        user=user,
        db=db,
    )

    delete_task(task.id, user=user, db=db)

    db.refresh(game)
    assert game.status == str(GameStatus.PUBLISHED)
    assert game.published_at is not None


def test_unpublish_game_archives_and_removes_public_access() -> None:
    db = next(make_session())
    user = add_user(db)
    task, game = add_publishable_task(db, user)
    publish_task(
        task.id,
        payload=PublishTaskRequest(title="正式标题", description="正式描述", tags=[]),
        user=user,
        db=db,
    )
    db.refresh(game)
    published_at = game.published_at

    response = unpublish_game(game.id, user=user, db=db)

    db.refresh(game)
    assert response.status == str(GameStatus.ARCHIVED)
    assert game.status == str(GameStatus.ARCHIVED)
    assert game.published_at == published_at
    assert list_games(status_filter=str(GameStatus.PUBLISHED), db=db) == []
    try:
        get_play_descriptor(game.id, db=db)
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 404
    else:
        raise AssertionError("Expected unpublished game to be inaccessible")


def test_archived_game_can_be_republished_without_resetting_published_at() -> None:
    db = next(make_session())
    user = add_user(db)
    task, game = add_publishable_task(db, user)
    publish_task(
        task.id,
        payload=PublishTaskRequest(title="正式标题", description="正式描述", tags=[]),
        user=user,
        db=db,
    )
    db.refresh(game)
    published_at = game.published_at
    unpublish_game(game.id, user=user, db=db)

    response = publish_task(
        task.id,
        payload=PublishTaskRequest(title="重新上架", description="重新描述", tags=["回归"]),
        user=user,
        db=db,
    )

    db.refresh(game)
    assert game.status == str(GameStatus.PUBLISHED)
    assert game.published_at == published_at
    assert response.result.gameStatus == str(GameStatus.PUBLISHED)
    assert response.result.title == "重新上架"


def test_update_game_rejects_non_owner() -> None:
    db = next(make_session())
    user = add_user(db)
    other_user = add_user(db, "other@example.com")
    _, game = add_publishable_task(db, user)

    try:
        update_game(
            game.id,
            payload=UpdateGameRequest(title="x", description="y", tags=[]),
            user=other_user,
            db=db,
        )
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 404
    else:
        raise AssertionError("Expected update_game to reject non-owner")


def test_publish_task_rejects_unfinished_task() -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user, status=TaskStatus.RUNNING)

    try:
        publish_task(
            task.id,
            payload=PublishTaskRequest(title="x", description="y", tags=[]),
            user=user,
            db=db,
        )
    except Exception as caught:
        assert getattr(caught, "status_code", None) == 400
    else:
        raise AssertionError("Expected publish_task to reject unfinished task")


def test_pipeline_canceled_task_does_not_become_failed(monkeypatch) -> None:
    db = next(make_session())
    user = add_user(db)
    task = add_task(db, user, status=TaskStatus.CANCELED)

    def session_factory() -> Session:
        return db

    monkeypatch.setattr(generation_pipeline, "SessionLocal", session_factory, raising=False)

    assert generation_pipeline.should_skip_task(task) is True
