from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.storage import get_minio_client, public_object_url
from app.models import Asset, User
from app.schemas.asset import AssetResponse

router = APIRouter(prefix="/assets", tags=["assets"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "text/plain",
    "application/json",
}


def safe_filename(filename: str) -> str:
    name = Path(filename or "asset").name.replace(" ", "-")
    return "".join(char for char in name if char.isalnum() or char in {"-", "_", "."}) or "asset"


@router.post("", response_model=AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssetResponse:
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {content_type}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    asset_id = str(uuid4())
    filename = safe_filename(file.filename or "asset")
    storage_key = f"uploads/{user.id}/{asset_id}/{filename}"

    client = get_minio_client()
    settings = get_settings()
    client.put_object(
        settings.minio_bucket,
        storage_key,
        BytesIO(content),
        length=len(content),
        content_type=content_type,
    )

    asset = Asset(
        id=asset_id,
        owner_user_id=user.id,
        filename=filename,
        content_type=content_type,
        size_bytes=len(content),
        storage_key=storage_key,
        public_url=public_object_url(storage_key),
        sha256=sha256(content).hexdigest(),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return AssetResponse(
        id=asset.id,
        filename=asset.filename,
        contentType=asset.content_type,
        sizeBytes=asset.size_bytes,
        url=asset.public_url,
    )
