from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

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
from app.schemas.task import AgentLogResponse, CreateTaskRequest, GenerationTaskResponse, TaskResult
from app.services.generation_pipeline import run_generation_pipeline

router = APIRouter(prefix="/generation-tasks", tags=["generation-tasks"])


def to_task_response(task: GenerationTask) -> GenerationTaskResponse:
    return GenerationTaskResponse(
        id=task.id,
        status=task.status,
        currentStep=task.current_step,
        ideaText=task.idea_text,
        assetIds=task.input_assets_json or [],
        result=TaskResult(gameId=task.result_game_id, manifestUrl=task.result_manifest_url),
        errorMessage=task.error_message,
    )


def get_owned_task(task_id: str, user: User, db: Session) -> GenerationTask:
    task = db.get(GenerationTask, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def validate_generation_snapshot(snapshot: dict) -> None:
    schema_version = snapshot.get("schemaVersion")
    if schema_version == "generated-game-bundle-v1":
        GeneratedGameBundleMetadata.model_validate(snapshot)
        return
    GameSpec.model_validate(snapshot)


@router.post("", response_model=GenerationTaskResponse)
def create_task(
    payload: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenerationTaskResponse:
    assets: list[Asset] = []
    for asset_id in payload.assetIds:
        asset = db.get(Asset, asset_id)
        if not asset or asset.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset not found: {asset_id}")
        assets.append(asset)

    task = GenerationTask(
        user_id=user.id,
        status=str(TaskStatus.PENDING),
        idea_text=payload.ideaText,
        input_assets_json=payload.assetIds,
        current_step=str(TaskStep.QUEUED),
    )
    db.add(task)
    db.flush()

    for asset in assets:
        if asset.generation_task_id is None:
            asset.generation_task_id = task.id

    db.add(AgentLog(task_id=task.id, level=str(AgentLogLevel.INFO), node_name=str(TaskStep.QUEUED), message="Queued generation task."))
    if assets:
        db.add(AgentLog(task_id=task.id, level=str(AgentLogLevel.INFO), node_name=str(TaskStep.QUEUED), message=f"Attached {len(assets)} uploaded assets to generation context."))
    db.commit()
    db.refresh(task)

    background_tasks.add_task(run_generation_pipeline, task.id, user.id)
    return to_task_response(task)


@router.get("/{task_id}", response_model=GenerationTaskResponse)
def get_task(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenerationTaskResponse:
    return to_task_response(get_owned_task(task_id, user, db))


@router.get("/{task_id}/logs", response_model=list[AgentLogResponse])
def get_task_logs(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AgentLogResponse]:
    task = get_owned_task(task_id, user, db)
    logs = db.scalars(select(AgentLog).where(AgentLog.task_id == task.id).order_by(AgentLog.created_at.asc())).all()
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenerationTaskResponse:
    task = get_owned_task(task_id, user, db)
    if task.status != TaskStatus.SUCCEEDED or not task.result_game_id or not task.result_manifest_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task is not ready to publish")

    game = db.get(Game, task.result_game_id)
    if not game or game.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated game not found")
    if not game.current_version_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generated game has no current version")

    version = db.get(GameVersion, game.current_version_id)
    if not version or version.game_id != game.id or version.generation_task_id != task.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generated game version is inconsistent")
    if PENDING_STORAGE_VALUE in {version.manifest_url, version.bundle_url, version.storage_prefix}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generated game artifacts are incomplete")
    if version.game_spec_json:
        validate_generation_snapshot(version.game_spec_json)

    if game.status != GameStatus.PUBLISHED:
        game.status = str(GameStatus.PUBLISHED)
        game.published_at = datetime.now(UTC)
        db.add(AgentLog(task_id=task.id, level=str(AgentLogLevel.INFO), node_name=str(TaskStep.PUBLISH), message="Published game to Home gallery."))
        db.commit()
    db.refresh(task)
    return to_task_response(task)
