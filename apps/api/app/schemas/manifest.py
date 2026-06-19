from pydantic import BaseModel, Field


class ManifestAsset(BaseModel):
    name: str
    url: str
    contentType: str


class ManifestPermissions(BaseModel):
    network: bool = False
    storage: bool = False


class GameManifest(BaseModel):
    schemaVersion: str = Field(default="game-manifest-v1")
    gameId: str
    versionId: str
    title: str
    entry: str
    entryUrl: str
    assets: list[ManifestAsset]
    permissions: ManifestPermissions = Field(default_factory=ManifestPermissions)
