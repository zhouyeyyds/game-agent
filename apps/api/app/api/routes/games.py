from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.constants import GameStatus
from app.core.database import get_db
from app.models import Game, GameVersion, User
from app.schemas.game import (
    AuthorResponse,
    GameListItem,
    PlayDescriptor,
    SandboxConfig,
    UpdateGameRequest,
)

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameListItem])
def list_games(
    status_filter: str = Query(default=str(GameStatus.PUBLISHED), alias="status"),
    db: Session = Depends(get_db),
) -> list[GameListItem]:
    games = db.scalars(
        select(Game).options(joinedload(Game.owner)).where(Game.status == status_filter).order_by(Game.published_at.desc())
    ).all()

    return [to_game_list_item(game) for game in games]


def to_game_list_item(game: Game) -> GameListItem:
    return GameListItem(
        id=game.id,
        title=game.title,
        description=game.description,
        coverUrl=game.cover_url,
        status=game.status,
        author=AuthorResponse(id=game.owner.id, displayName=game.owner.display_name),
        tags=game.tags or [],
        publishedAt=game.published_at.isoformat() if game.published_at else None,
        playCount=game.play_count,
    )


@router.patch("/{game_id}", response_model=GameListItem)
def update_game(
    game_id: str,
    payload: UpdateGameRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GameListItem:
    game = db.scalar(select(Game).options(joinedload(Game.owner)).where(Game.id == game_id))
    if not game or game.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    game.title = payload.title
    game.description = payload.description
    game.cover_url = payload.coverUrl
    game.tags = payload.tags
    db.commit()
    db.refresh(game)
    return to_game_list_item(game)


@router.post("/{game_id}/unpublish", response_model=GameListItem)
def unpublish_game(
    game_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GameListItem:
    game = db.scalar(select(Game).options(joinedload(Game.owner)).where(Game.id == game_id))
    if not game or game.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    if game.status != str(GameStatus.PUBLISHED):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is not published")

    game.status = str(GameStatus.ARCHIVED)
    db.commit()
    db.refresh(game)
    return to_game_list_item(game)


@router.get("/{game_id}/play", response_model=PlayDescriptor)
def get_play_descriptor(game_id: str, db: Session = Depends(get_db)) -> PlayDescriptor:
    game = db.get(Game, game_id)
    if not game or game.status != str(GameStatus.PUBLISHED):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    version = db.get(GameVersion, game.current_version_id) if game.current_version_id else None
    if not version:
        version = db.scalar(
            select(GameVersion)
            .where(GameVersion.game_id == game.id)
            .order_by(GameVersion.version_number.desc())
        )
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game version not found")

    game.play_count += 1
    db.commit()

    return PlayDescriptor(
        gameId=game.id,
        title=game.title,
        description=game.description,
        coverUrl=game.cover_url,
        tags=game.tags or [],
        publishedAt=game.published_at.isoformat() if game.published_at else None,
        playCount=game.play_count,
        manifestUrl=version.manifest_url,
        storagePrefix=version.storage_prefix,
        sandbox=SandboxConfig(),
    )
