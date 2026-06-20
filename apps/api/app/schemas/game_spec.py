from typing import Literal

from pydantic import BaseModel, Field, model_validator

DANGEROUS_TEXT_MARKERS = ("<script", "</script", "javascript:")


def validate_safe_text(value: str, field_name: str) -> None:
    lowered = value.lower()
    if any(marker in lowered for marker in DANGEROUS_TEXT_MARKERS):
        raise ValueError(f"{field_name} contains unsafe text")


class ThemeSpec(BaseModel):
    background: str = "#10111f"
    primary: str = "#65e4ff"
    accent: str = "#ffcc66"


class ChoiceSpec(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    nextSceneId: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_text(self) -> "ChoiceSpec":
        validate_safe_text(self.label, "choice.label")
        return self


class SceneSpec(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=1600)
    choices: list[ChoiceSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_text(self) -> "SceneSpec":
        validate_safe_text(self.title, "scene.title")
        validate_safe_text(self.body, "scene.body")
        return self


class EndingSpec(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=1600)
    result: Literal["win", "lose", "neutral"] = "neutral"

    @model_validator(mode="after")
    def validate_text(self) -> "EndingSpec":
        validate_safe_text(self.title, "ending.title")
        validate_safe_text(self.body, "ending.body")
        return self


class GameSpec(BaseModel):
    schemaVersion: Literal["game-spec-v1"] = "game-spec-v1"
    template: Literal["choice_adventure"] = "choice_adventure"
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1200)
    tags: list[str] = Field(default_factory=list, max_length=12)
    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    startSceneId: str = Field(min_length=1, max_length=120)
    scenes: list[SceneSpec] = Field(min_length=1)
    endings: list[EndingSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_graph(self) -> "GameSpec":
        validate_safe_text(self.title, "title")
        validate_safe_text(self.description, "description")

        scene_ids = [scene.id for scene in self.scenes]
        ending_ids = [ending.id for ending in self.endings]
        if len(scene_ids) != len(set(scene_ids)):
            raise ValueError("scene ids must be unique")
        if len(ending_ids) != len(set(ending_ids)):
            raise ValueError("ending ids must be unique")
        if self.startSceneId not in scene_ids:
            raise ValueError("startSceneId must reference a scene")

        valid_targets = set(scene_ids) | set(ending_ids)
        for scene in self.scenes:
            for choice in scene.choices:
                if choice.nextSceneId not in valid_targets:
                    raise ValueError(f"choice target not found: {choice.nextSceneId}")

        if not self._has_reachable_ending():
            raise ValueError("at least one ending must be reachable from startSceneId")
        return self

    def _has_reachable_ending(self) -> bool:
        scenes_by_id = {scene.id: scene for scene in self.scenes}
        ending_ids = {ending.id for ending in self.endings}
        seen: set[str] = set()
        stack = [self.startSceneId]

        while stack:
            current = stack.pop()
            if current in ending_ids:
                return True
            if current in seen:
                continue
            seen.add(current)
            scene = scenes_by_id.get(current)
            if not scene:
                continue
            stack.extend(choice.nextSceneId for choice in scene.choices)
        return False
