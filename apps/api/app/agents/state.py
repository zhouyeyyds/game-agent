from typing import Any, TypedDict

from app.schemas.generated_bundle import GeneratedGameBundle


class GenerationState(TypedDict, total=False):
    task_id: str
    user_id: str
    idea_text: str
    asset_ids: list[str]
    asset_context: list[dict[str, Any]]
    idea_brief: dict[str, Any]
    requirement_profile: dict[str, Any]
    design_doc: dict[str, Any]
    bundle_json: dict[str, Any]
    bundle: GeneratedGameBundle
    security_errors: list[str]
    repair_attempts: int
    game_id: str
    version_id: str
    manifest_url: str
    error_message: str
