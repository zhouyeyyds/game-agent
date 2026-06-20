from app.agents.llm import _extract_json_object
from app.agents.nodes import build_mock_spec, render_bundle
from app.schemas.game_spec import GameSpec


def test_extract_json_object_from_markdown_fence() -> None:
    assert _extract_json_object('```json\n{"ok": true}\n```') == {"ok": True}


def test_mock_spec_renders_remote_bundle_files() -> None:
    spec = build_mock_spec("生成一个森林逃脱互动游戏")

    GameSpec.model_validate(spec.model_dump())
    files = render_bundle(spec)

    assert set(files) == {"index.html", "game.js", "styles.css", "spec.json"}
    assert "game-spec-v1" in files["index.html"]
