from pydantic import BaseModel, ConfigDict


class AuthorResponse(BaseModel):
    id: str
    displayName: str


class GameListItem(BaseModel):
    id: str
    title: str
    description: str
    coverUrl: str | None
    author: AuthorResponse
    tags: list[str]
    publishedAt: str | None
    playCount: int


class SandboxConfig(BaseModel):
    allowScripts: bool = True
    allowSameOrigin: bool = False
    allowForms: bool = False
    allowPopups: bool = False


class PlayDescriptor(BaseModel):
    gameId: str
    title: str
    runtime: str = "iframe_manifest_v1"
    manifestUrl: str
    storagePrefix: str
    sandbox: SandboxConfig


class GameModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    status: str
