from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.constants import GameStatus
from app.core.database import get_db
from app.models import Game, GameVersion
from app.schemas.game import AuthorResponse, GameListItem, PlayDescriptor, SandboxConfig

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameListItem])
def list_games(
    status_filter: str = Query(default=str(GameStatus.PUBLISHED), alias="status"),
    db: Session = Depends(get_db),
) -> list[GameListItem]:
    games = db.scalars(
        select(Game).options(joinedload(Game.owner)).where(Game.status == status_filter).order_by(Game.published_at.desc())
    ).all()

    return [
        GameListItem(
            id=game.id,
            title=game.title,
            description=game.description,
            coverUrl=game.cover_url,
            author=AuthorResponse(id=game.owner.id, displayName=game.owner.display_name),
            tags=game.tags or [],
            publishedAt=game.published_at.isoformat() if game.published_at else None,
            playCount=game.play_count,
        )
        for game in games
    ]


@router.get("/{game_id}/play", response_model=PlayDescriptor)
def get_play_descriptor(game_id: str, db: Session = Depends(get_db)) -> PlayDescriptor:
    game = db.get(Game, game_id)
    if not game or game.status != GameStatus.PUBLISHED:
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
        manifestUrl=version.manifest_url,
        storagePrefix=version.storage_prefix,
        sandbox=SandboxConfig(),
    )
