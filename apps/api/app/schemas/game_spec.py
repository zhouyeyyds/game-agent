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


class PlayerSpec(BaseModel):
    label: str = Field(default="Player", min_length=1, max_length=80)
    color: str = "#65e4ff"
    speed: int = Field(default=260, ge=120, le=520)

    @model_validator(mode="after")
    def validate_text(self) -> "PlayerSpec":
        validate_safe_text(self.label, "player.label")
        return self


class WorldSpec(BaseModel):
    width: int = Field(default=960, ge=640, le=1600)
    height: int = Field(default=540, ge=360, le=1000)
    timeLimitSeconds: int = Field(default=90, ge=30, le=300)


class GoalSpec(BaseModel):
    label: str = Field(default="Exit", min_length=1, max_length=80)
    x: int = Field(default=880, ge=0, le=1600)
    y: int = Field(default=460, ge=0, le=1000)
    radius: int = Field(default=28, ge=12, le=80)
    color: str = "#ffcc66"

    @model_validator(mode="after")
    def validate_text(self) -> "GoalSpec":
        validate_safe_text(self.label, "goal.label")
        return self


class ObstacleSpec(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    label: str = Field(default="Obstacle", min_length=1, max_length=80)
    x: int = Field(ge=0, le=1600)
    y: int = Field(ge=0, le=1000)
    width: int = Field(default=80, ge=20, le=320)
    height: int = Field(default=80, ge=20, le=320)
    vx: int = Field(default=0, ge=-260, le=260)
    vy: int = Field(default=0, ge=-260, le=260)
    color: str = "#ff4f6d"

    @model_validator(mode="after")
    def validate_text(self) -> "ObstacleSpec":
        validate_safe_text(self.label, "obstacle.label")
        return self


class CollectibleSpec(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    label: str = Field(default="Token", min_length=1, max_length=80)
    x: int = Field(ge=0, le=1600)
    y: int = Field(ge=0, le=1000)
    radius: int = Field(default=16, ge=8, le=48)
    points: int = Field(default=10, ge=1, le=100)
    color: str = "#a7f3d0"

    @model_validator(mode="after")
    def validate_text(self) -> "CollectibleSpec":
        validate_safe_text(self.label, "collectible.label")
        return self


class ArcadeSpec(BaseModel):
    player: PlayerSpec = Field(default_factory=PlayerSpec)
    world: WorldSpec = Field(default_factory=WorldSpec)
    goal: GoalSpec = Field(default_factory=GoalSpec)
    obstacles: list[ObstacleSpec] = Field(default_factory=list, max_length=12)
    collectibles: list[CollectibleSpec] = Field(default_factory=list, max_length=12)
    instructions: str = Field(
        default="Use arrow keys or WASD to move. Collect tokens and reach the goal.",
        min_length=1,
        max_length=400,
    )
    winText: str = Field(default="You escaped.", min_length=1, max_length=240)
    loseText: str = Field(default="Try again.", min_length=1, max_length=240)

    @model_validator(mode="after")
    def validate_arcade(self) -> "ArcadeSpec":
        validate_safe_text(self.instructions, "arcade.instructions")
        validate_safe_text(self.winText, "arcade.winText")
        validate_safe_text(self.loseText, "arcade.loseText")

        obstacle_ids = [obstacle.id for obstacle in self.obstacles]
        collectible_ids = [collectible.id for collectible in self.collectibles]
        if len(obstacle_ids) != len(set(obstacle_ids)):
            raise ValueError("obstacle ids must be unique")
        if len(collectible_ids) != len(set(collectible_ids)):
            raise ValueError("collectible ids must be unique")
        return self


class GameSpec(BaseModel):
    schemaVersion: Literal["game-spec-v1"] = "game-spec-v1"
    template: Literal["choice_adventure", "canvas_arcade"] = "canvas_arcade"
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1200)
    tags: list[str] = Field(default_factory=list, max_length=12)
    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    startSceneId: str | None = Field(default=None, min_length=1, max_length=120)
    scenes: list[SceneSpec] = Field(default_factory=list)
    endings: list[EndingSpec] = Field(default_factory=list)
    arcade: ArcadeSpec | None = None

    @model_validator(mode="after")
    def validate_graph(self) -> "GameSpec":
        validate_safe_text(self.title, "title")
        validate_safe_text(self.description, "description")

        if self.template == "canvas_arcade":
            if self.arcade is None:
                raise ValueError("canvas_arcade requires arcade")
            return self

        if not self.startSceneId:
            raise ValueError("choice_adventure requires startSceneId")
        if not self.scenes:
            raise ValueError("choice_adventure requires scenes")
        if not self.endings:
            raise ValueError("choice_adventure requires endings")

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
