from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ManifestAsset(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    url: str = Field(min_length=1, max_length=1024)
    contentType: str = Field(min_length=1, max_length=120)


class ManifestPermissions(BaseModel):
    network: bool = False
    storage: bool = False


class GameManifest(BaseModel):
    schemaVersion: Literal["game-manifest-v1"] = "game-manifest-v1"
    gameId: str = Field(min_length=1)
    versionId: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)
    entry: Literal["index.html"] = "index.html"
    entryUrl: str = Field(min_length=1, max_length=1024)
    assets: list[ManifestAsset] = Field(default_factory=list)
    permissions: ManifestPermissions = Field(default_factory=ManifestPermissions)

    @model_validator(mode="after")
    def validate_assets(self) -> "GameManifest":
        names = [asset.name for asset in self.assets]
        if len(names) != len(set(names)):
            raise ValueError("manifest asset names must be unique")
        return self
