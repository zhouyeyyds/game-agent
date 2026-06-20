from pydantic import BaseModel, ConfigDict
from pydantic import Field


class AuthorResponse(BaseModel):
    id: str
    displayName: str


class GameListItem(BaseModel):
    id: str
    title: str
    description: str
    coverUrl: str | None
    status: str
    author: AuthorResponse
    tags: list[str]
    publishedAt: str | None
    playCount: int


class SandboxConfig(BaseModel):
    allowScripts: bool = True
    allowSameOrigin: bool = False
    allowForms: bool = False
    allowPopups: bool = False


class UpdateGameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    coverUrl: str | None = Field(default=None, max_length=512)
    tags: list[str] = Field(default_factory=list, max_length=12)


class PlayDescriptor(BaseModel):
    gameId: str
    title: str
    description: str
    coverUrl: str | None
    tags: list[str]
    publishedAt: str | None
    playCount: int
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
