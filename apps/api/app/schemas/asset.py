from pydantic import BaseModel


class AssetResponse(BaseModel):
    id: str
    filename: str
    contentType: str
    sizeBytes: int
    url: str
