from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, object_session

from app.api.deps import get_current_user
from app.core.constants import (
    PENDING_STORAGE_VALUE,
    AgentLogLevel,
    GameStatus,
    TaskStatus,
    TaskStep,
)
from app.core.database import get_db
from app.models import AgentLog, Asset, Game, GameVersion, GenerationTask, User
from app.schemas.game_spec import GameSpec
from app.schemas.generated_bundle import GeneratedGameBundleMetadata
from app.schemas.task import (
    AgentLogResponse,
    CreateTaskRequest,
    GenerationTaskResponse,
    PublishTaskRequest,
    TaskMetrics,
    TaskResult,
)
from app.services.generation_pipeline import run_generation_pipeline

router = APIRouter(prefix="/generation-tasks", tags=["generation-tasks"])

ACTIVE_TASK_STATUSES = {str(TaskStatus.PENDING), str(TaskStatus.RUNNING)}
RETRYABLE_TASK_STATUSES = {
    str(TaskStatus.SUCCEEDED),
    str(TaskStatus.FAILED),
    str(TaskStatus.CANCELED),
}

CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
StatusFilter = Annotated[str | None, Query(alias="status")]


def to_task_response(task: GenerationTask) -> GenerationTaskResponse:
    result = TaskResult(gameId=task.result_game_id, manifestUrl=task.result_manifest_url)
    if task.result_game_id:
        session = object_session(task)
        game = session.get(Game, task.result_game_id) if session else None
        if game:
            result = TaskResult(
                gameId=task.result_game_id,
                manifestUrl=task.result_manifest_url,
                publishedAt=game.published_at.isoformat() if game.published_at else None,
                title=game.title,
                description=game.description,
                coverUrl=game.cover_url,
                tags=game.tags or [],
                gameStatus=game.status,
            )

    return GenerationTaskResponse(
        id=task.id,
        status=task.status,
        currentStep=task.current_step,
        ideaText=task.idea_text,
        assetIds=task.input_assets_json or [],
        result=result,
        metrics=TaskMetrics(
            agentStepCount=task.agent_step_count or 0,
            modelCallCount=task.model_call_count or 0,
            promptTokens=task.prompt_tokens or 0,
            completionTokens=task.completion_tokens or 0,
            totalTokens=task.total_tokens or 0,
            estimatedCostUsd=task.estimated_cost_usd,
        ),
        errorMessage=task.error_message,
        createdAt=task.created_at.isoformat() if task.created_at else None,
        startedAt=task.started_at.isoformat() if task.started_at else None,
        finishedAt=task.finished_at.isoformat() if task.finished_at else None,
        retriedFromTaskId=task.retried_from_task_id,
    )


def get_owned_task(task_id: str, user: User, db: Session) -> GenerationTask:
    task = db.get(GenerationTask, task_id)
    if not task or task.user_id != user.id or task.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def validate_generation_snapshot(snapshot: dict) -> None:
    schema_version = snapshot.get("schemaVersion")
    if schema_version == "generated-game-bundle-v1":
        GeneratedGameBundleMetadata.model_validate(snapshot)
        return
    GameSpec.model_validate(snapshot)


def create_generation_task_record(
    *,
    db: Session,
    user: User,
    idea_text: str,
    asset_ids: list[str],
    retried_from_task_id: str | None = None,
) -> GenerationTask:
    assets: list[Asset] = []
    for asset_id in asset_ids:
        asset = db.get(Asset, asset_id)
        if not asset or asset.owner_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset not found: {asset_id}",
            )
        assets.append(asset)

    task = GenerationTask(
        user_id=user.id,
        retried_from_task_id=retried_from_task_id,
        status=str(TaskStatus.PENDING),
        idea_text=idea_text,
        input_assets_json=asset_ids,
        current_step=str(TaskStep.QUEUED),
    )
    db.add(task)
    db.flush()

    for asset in assets:
        if asset.generation_task_id is None:
            asset.generation_task_id = task.id

    db.add(
        AgentLog(
            task_id=task.id,
            level=str(AgentLogLevel.INFO),
            node_name=str(TaskStep.QUEUED),
            message="Queued generation task.",
        )
    )
    if retried_from_task_id:
        db.add(
            AgentLog(
                task_id=task.id,
                level=str(AgentLogLevel.INFO),
                node_name=str(TaskStep.QUEUED),
                message=f"Retry task created from {retried_from_task_id}.",
            )
        )
    if assets:
        db.add(
            AgentLog(
                task_id=task.id,
                level=str(AgentLogLevel.INFO),
                node_name=str(TaskStep.QUEUED),
                message=f"Attached {len(assets)} uploaded assets to generation context.",
            )
        )
    db.commit()
    db.refresh(task)
    return task


@router.post("", response_model=GenerationTaskResponse)
def create_task(
    payload: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    db: DbSession,
) -> GenerationTaskResponse:
    task = create_generation_task_record(
        db=db,
        user=user,
        idea_text=payload.ideaText,
        asset_ids=payload.assetIds,
    )

    background_tasks.add_task(run_generation_pipeline, task.id, user.id)
    return to_task_response(task)


@router.get("", response_model=list[GenerationTaskResponse])
def list_tasks(
    user: CurrentUser,
    db: DbSession,
    limit: int = 20,
    offset: int = 0,
    status_filter: StatusFilter = None,
) -> list[GenerationTaskResponse]:
    bounded_limit = min(max(limit, 1), 100)
    bounded_offset = max(offset, 0)
    query = select(GenerationTask).where(
        GenerationTask.user_id == user.id,
        GenerationTask.deleted_at.is_(None),
    )
    if status_filter:
        query = query.where(GenerationTask.status == status_filter)
    tasks = db.scalars(
        query.order_by(GenerationTask.created_at.desc())
        .offset(bounded_offset)
        .limit(bounded_limit)
    ).all()
    return [to_task_response(task) for task in tasks]


@router.get("/{task_id}", response_model=GenerationTaskResponse)
def get_task(
    task_id: str,
    user: CurrentUser,
    db: DbSession,
) -> GenerationTaskResponse:
    return to_task_response(get_owned_task(task_id, user, db))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    user: CurrentUser,
    db: DbSession,
) -> Response:
    task = get_owned_task(task_id, user, db)
    if task.status in ACTIVE_TASK_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active task cannot be deleted",
        )

    task.deleted_at = datetime.now(UTC)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/cancel", response_model=GenerationTaskResponse)
def cancel_task(
    task_id: str,
    user: CurrentUser,
    db: DbSession,
) -> GenerationTaskResponse:
    task = get_owned_task(task_id, user, db)
    if task.status not in ACTIVE_TASK_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be canceled",
        )

    task.status = str(TaskStatus.CANCELED)
    task.error_message = "Generation task was canceled by the creator."
    task.finished_at = datetime.now(UTC)
    db.add(
        AgentLog(
            task_id=task.id,
            level=str(AgentLogLevel.INFO),
            node_name=task.current_step,
            message="Canceled generation task by creator request.",
        )
    )
    db.commit()
    db.refresh(task)
    return to_task_response(task)


@router.post("/{task_id}/retry", response_model=GenerationTaskResponse)
def retry_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    db: DbSession,
) -> GenerationTaskResponse:
    source_task = get_owned_task(task_id, user, db)
    if source_task.status not in RETRYABLE_TASK_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be retried",
        )

    task = create_generation_task_record(
        db=db,
        user=user,
        idea_text=source_task.idea_text,
        asset_ids=source_task.input_assets_json or [],
        retried_from_task_id=source_task.id,
    )
    background_tasks.add_task(run_generation_pipeline, task.id, user.id)
    return to_task_response(task)


@router.get("/{task_id}/logs", response_model=list[AgentLogResponse])
def get_task_logs(
    task_id: str,
    user: CurrentUser,
    db: DbSession,
) -> list[AgentLogResponse]:
    task = get_owned_task(task_id, user, db)
    logs = db.scalars(
        select(AgentLog)
        .where(AgentLog.task_id == task.id)
        .order_by(AgentLog.created_at.asc())
    ).all()
    return [
        AgentLogResponse(
            id=log.id,
            level=log.level,
            nodeName=log.node_name,
            message=log.message,
            createdAt=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.post("/{task_id}/publish", response_model=GenerationTaskResponse)
def publish_task(
    task_id: str,
    payload: PublishTaskRequest,
    user: CurrentUser,
    db: DbSession,
) -> GenerationTaskResponse:
    task = get_owned_task(task_id, user, db)
    if (
        task.status != str(TaskStatus.SUCCEEDED)
        or not task.result_game_id
        or not task.result_manifest_url
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not ready to publish",
        )

    game = db.get(Game, task.result_game_id)
    if not game or game.owner_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated game not found",
        )
    if not game.current_version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generated game has no current version",
        )

    version = db.get(GameVersion, game.current_version_id)
    if (
        not version
        or version.game_id != game.id
        or version.generation_task_id != task.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generated game version is inconsistent",
        )
    if PENDING_STORAGE_VALUE in {
        version.manifest_url,
        version.bundle_url,
        version.storage_prefix,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generated game artifacts are incomplete",
        )
    if version.game_spec_json:
        validate_generation_snapshot(version.game_spec_json)

    game.title = payload.title
    game.description = payload.description
    game.cover_url = payload.coverUrl
    game.tags = payload.tags

    if game.status != str(GameStatus.PUBLISHED):
        game.status = str(GameStatus.PUBLISHED)
        if game.published_at is None:
            game.published_at = datetime.now(UTC)
        db.add(
            AgentLog(
                task_id=task.id,
                level=str(AgentLogLevel.INFO),
                node_name=str(TaskStep.PUBLISH),
                message="Published game to Home gallery.",
            )
        )
    db.commit()
    db.refresh(task)
    return to_task_response(task)
