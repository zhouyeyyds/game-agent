import pytest

from app.agents.llm import _extract_json_object
from app.agents.nodes import derive_requirement_profile, scan_bundle_security
from app.schemas.generated_bundle import GeneratedGameBundle


def valid_bundle(**overrides) -> dict:
    bundle = {
        "schemaVersion": "generated-game-bundle-v1",
        "title": "星港突围",
        "description": "太空飞船弹幕躲避小游戏",
        "tags": ["arcade", "space"],
        "entry": "index.html",
        "permissions": {"network": False, "storage": False, "externalScripts": False},
        "files": [
            {
                "path": "index.html",
                "contentType": "text/html",
                "content": (
                    "<!doctype html><html><head><link rel=\"stylesheet\" "
                    "href=\"styles.css\"></head><body><canvas id=\"game\"></canvas>"
                    "<script src=\"game.js\"></script></body></html>"
                ),
            },
            {
                "path": "game.js",
                "contentType": "application/javascript",
                "content": "const canvas = document.getElementById('game');",
            },
            {
                "path": "styles.css",
                "contentType": "text/css",
                "content": "html, body { margin: 0; }",
            },
        ],
    }
    bundle.update(overrides)
    return bundle


def test_extract_json_object_from_markdown_fence() -> None:
    assert _extract_json_object('```json\n{"ok": true}\n```') == {"ok": True}


def test_generated_bundle_accepts_valid_static_files() -> None:
    bundle = GeneratedGameBundle.model_validate(valid_bundle())

    assert bundle.entry == "index.html"
    assert scan_bundle_security(bundle) == []
    assert bundle.metadata_json()["files"][0]["path"] == "index.html"


def test_generated_bundle_requires_index_html() -> None:
    payload = valid_bundle(files=[valid_bundle()["files"][1]])

    with pytest.raises(ValueError, match="index.html"):
        GeneratedGameBundle.model_validate(payload)


def test_generated_bundle_rejects_parent_paths() -> None:
    payload = valid_bundle(
        files=[
            valid_bundle()["files"][0],
            {
                "path": "../secret.txt",
                "contentType": "text/plain",
                "content": "secret",
            },
        ]
    )

    with pytest.raises(ValueError, match="parent path|not allowed"):
        GeneratedGameBundle.model_validate(payload)


def test_security_scan_rejects_external_script() -> None:
    payload = valid_bundle()
    payload["files"][0]["content"] = '<script src="https://cdn.example.com/game.js"></script>'
    bundle = GeneratedGameBundle.model_validate(payload)

    assert scan_bundle_security(bundle)


def test_security_scan_rejects_dangerous_js_apis() -> None:
    payload = valid_bundle()
    payload["files"][1]["content"] = "fetch('/x'); eval('1'); localStorage.setItem('x', 'y');"
    bundle = GeneratedGameBundle.model_validate(payload)
    errors = scan_bundle_security(bundle)

    assert any("fetch" in error for error in errors)
    assert any("eval" in error for error in errors)
    assert any("localStorage" in error for error in errors)


def test_requirement_profile_extracts_prompt_intent() -> None:
    profile = derive_requirement_profile("困难太空射击弹幕游戏")

    assert profile["genre"] == "shooter"
    assert profile["setting"] == "space"
    assert profile["difficulty"] == "hard"
