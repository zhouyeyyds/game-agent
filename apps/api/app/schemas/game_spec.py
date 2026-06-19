from typing import Literal

from pydantic import BaseModel, Field


class ThemeSpec(BaseModel):
    background: str = "#10111f"
    primary: str = "#65e4ff"
    accent: str = "#ffcc66"


class ChoiceSpec(BaseModel):
    label: str
    nextSceneId: str


class SceneSpec(BaseModel):
    id: str
    title: str
    body: str
    choices: list[ChoiceSpec] = Field(default_factory=list)


class EndingSpec(BaseModel):
    id: str
    title: str
    body: str
    result: Literal["win", "lose", "neutral"] = "neutral"


class GameSpec(BaseModel):
    schemaVersion: Literal["game-spec-v1"] = "game-spec-v1"
    template: Literal["choice_adventure"] = "choice_adventure"
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    startSceneId: str
    scenes: list[SceneSpec]
    endings: list[EndingSpec]
