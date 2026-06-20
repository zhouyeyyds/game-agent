from typing import Any, TypedDict

from app.schemas.game_spec import GameSpec


class GenerationState(TypedDict, total=False):
    task_id: str
    user_id: str
    idea_text: str
    asset_ids: list[str]
    asset_context: list[dict[str, Any]]
    idea_brief: dict[str, Any]
    design_doc: dict[str, Any]
    spec_json: dict[str, Any]
    spec: GameSpec
    validation_errors: list[str]
    repair_attempts: int
    files: dict[str, str]
    game_id: str
    version_id: str
    manifest_url: str
    error_message: str

