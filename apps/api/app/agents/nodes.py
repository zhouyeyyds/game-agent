from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from textwrap import dedent
from typing import Any

from sqlalchemy.orm import Session

from app.agents.llm import generate_json
from app.agents.state import GenerationState
from app.core.constants import (
    PENDING_STORAGE_VALUE,
    AgentLogLevel,
    GameStatus,
    TaskStatus,
    TaskStep,
)
from app.core.storage import public_object_url, upload_text_object
from app.models import AgentLog, Asset, Game, GameVersion, GenerationTask, User
from app.schemas.generated_bundle import GeneratedGameBundle
from app.schemas.manifest import GameManifest, ManifestAsset, ManifestPermissions

SECURITY_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"<script[^>]+src\s*=\s*['\"]?https?://", "external script src is not allowed"),
    (r"<link[^>]+href\s*=\s*['\"]?https?://", "external stylesheet href is not allowed"),
    (r"\bfetch\s*\(", "fetch is not allowed"),
    (r"\bXMLHttpRequest\b", "XMLHttpRequest is not allowed"),
    (r"\bWebSocket\b", "WebSocket is not allowed"),
    (r"\bEventSource\b", "EventSource is not allowed"),
    (r"\beval\s*\(", "eval is not allowed"),
    (r"\bnew\s+Function\s*\(", "new Function is not allowed"),
    (r"\bimport\s*\(", "dynamic import is not allowed"),
    (r"\bdocument\.cookie\b", "document.cookie is not allowed"),
    (r"\blocalStorage\b", "localStorage is not allowed"),
    (r"\bsessionStorage\b", "sessionStorage is not allowed"),
    (r"<\s*iframe\b", "iframe is not allowed"),
    (r"<\s*object\b", "object is not allowed"),
    (r"<\s*embed\b", "embed is not allowed"),
)


class GenerationCanceled(RuntimeError):
    pass


def ensure_task_not_canceled(db: Session, task: GenerationTask) -> None:
    db.refresh(task)
    if task.status == TaskStatus.CANCELED:
        raise GenerationCanceled("Generation task was canceled")


def add_log(
    db: Session,
    task: GenerationTask,
    node_name: str,
    message: str,
    level: str = AgentLogLevel.INFO,
    payload: dict[str, Any] | None = None,
) -> None:
    db.add(
        AgentLog(
            task_id=task.id,
            level=str(level),
            node_name=str(node_name),
            message=message,
            payload_json=payload,
        )
    )
    db.commit()


def update_step(
    db: Session,
    task: GenerationTask,
    step: str,
    status: TaskStatus = TaskStatus.RUNNING,
) -> None:
    ensure_task_not_canceled(db, task)
    task.status = str(status)
    task.current_step = str(step)
    if not task.started_at:
        task.started_at = datetime.now(UTC)
    db.commit()
    db.refresh(task)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def derive_requirement_profile(
    prompt: str,
    asset_context: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    asset_context = asset_context or []
    genre = "custom_web_game"
    if _contains_any(prompt, ("跑酷", "parkour", "runner", "race", "赛车", "竞速")):
        genre = "runner"
    elif _contains_any(prompt, ("贪吃蛇", "snake")):
        genre = "snake"
    elif _contains_any(prompt, ("打砖块", "breakout", "brick")):
        genre = "breakout"
    elif _contains_any(prompt, ("平台", "platformer", "跳跃")):
        genre = "platformer"
    elif _contains_any(prompt, ("射击", "shoot", "bullet", "弹幕", "飞机")):
        genre = "shooter"
    elif _contains_any(prompt, ("卡牌", "card", "回合制", "turn")):
        genre = "turn_based"
    elif _contains_any(prompt, ("迷宫", "maze", "解谜", "puzzle", "钥匙", "机关")):
        genre = "puzzle"

    setting = "original"
    if _contains_any(prompt, ("森林", "forest", "丛林", "jungle")):
        setting = "forest"
    elif _contains_any(prompt, ("太空", "space", "星球", "宇宙", "飞船")):
        setting = "space"
    elif _contains_any(prompt, ("海底", "ocean", "深海", "水下")):
        setting = "underwater"
    elif _contains_any(prompt, ("校园", "school", "教室")):
        setting = "school"
    elif _contains_any(prompt, ("恐怖", "horror", "鬼", "诡异")):
        setting = "haunted"

    difficulty = "normal"
    if _contains_any(prompt, ("困难", "hard", "高难", "极限")):
        difficulty = "hard"
    elif _contains_any(prompt, ("简单", "easy", "休闲", "轻松")):
        difficulty = "easy"

    return {
        "genre": genre,
        "setting": setting,
        "difficulty": difficulty,
        "assetCount": len(asset_context),
        "sourcePrompt": prompt[:500],
    }


def load_asset_context(db: Session, task: GenerationTask) -> list[dict[str, Any]]:
    assets = []
    for asset_id in task.input_assets_json or []:
        asset = db.get(Asset, asset_id)
        if not asset:
            continue
        assets.append(
            {
                "id": asset.id,
                "filename": asset.filename,
                "contentType": asset.content_type,
                "sizeBytes": asset.size_bytes,
                "url": asset.public_url,
            }
        )
    return assets


def idea_analyzer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.IDEA)
    asset_context = load_asset_context(db, task)
    profile = derive_requirement_profile(state["idea_text"], asset_context)
    brief = {
        "coreIdea": state["idea_text"][:500],
        "targetFormat": "generated-game-bundle-v1",
        "genre": profile["genre"],
        "setting": profile["setting"],
        "difficulty": profile["difficulty"],
        "requiredQualities": [
            "self-contained static web game",
            "clear controls",
            "playable win and lose states",
            "no external resources",
        ],
    }
    add_log(
        db,
        task,
        "idea_analyzer",
        f"Analyzed creator prompt and found {len(asset_context)} uploaded asset reference(s).",
        payload={"brief": brief, "profile": profile, "assets": asset_context},
    )
    return {"asset_context": asset_context, "idea_brief": brief, "requirement_profile": profile}


def asset_interpreter(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    asset_context = state.get("asset_context", [])
    interpreted = [
        {
            **asset,
            "intendedUse": "reference material for theme, mechanics, characters, or UI style",
        }
        for asset in asset_context
    ]
    add_log(
        db,
        task,
        "asset_interpreter",
        f"Prepared {len(interpreted)} asset reference(s) for code generation.",
        payload={"assets": interpreted},
    )
    return {"asset_context": interpreted}


def game_designer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.SPEC)
    profile = state.get("requirement_profile", derive_requirement_profile(state["idea_text"]))
    design_doc = {
        "format": "generated-game-bundle-v1",
        "genre": profile["genre"],
        "setting": profile["setting"],
        "difficulty": profile["difficulty"],
        "allowedFiles": ["index.html", "game.js", "styles.css", "data/*.json"],
        "constraints": [
            "Generate a complete playable browser game, not a static mockup.",
            "Use only vanilla HTML, CSS and JavaScript.",
            "Do not use external URLs, CDNs, network requests, storage APIs or eval.",
            "Keep all code self-contained in the returned files.",
            "Include clear controls, scoring or progress, and win/lose feedback.",
        ],
    }
    add_log(
        db,
        task,
        "game_designer",
        "Planned static web bundle constraints and target gameplay.",
        payload=design_doc,
    )
    return {"design_doc": design_doc}


BUNDLE_SYSTEM_PROMPT = dedent(
    """
    You are a senior browser game engineer. Generate a complete, self-contained
    static web game as one JSON object matching generated-game-bundle-v1.

    Required JSON shape:
    {
      "schemaVersion": "generated-game-bundle-v1",
      "title": "string",
      "description": "string",
      "tags": ["string"],
      "entry": "index.html",
      "permissions": {"network": false, "storage": false, "externalScripts": false},
      "files": [
        {"path": "index.html", "contentType": "text/html", "content": "..."},
        {"path": "game.js", "contentType": "application/javascript", "content": "..."},
        {"path": "styles.css", "contentType": "text/css", "content": "..."}
      ]
    }

    Rules:
    - Return JSON only. No markdown.
    - Use only index.html, game.js, styles.css, and optional data/*.json.
    - Use vanilla browser APIs only. Do not use external libraries.
    - Keep the bundle compact: prefer exactly index.html, game.js and styles.css.
    - Keep total generated content under 80 KB unless the user explicitly asks for
      a larger game.
    - Build a focused playable prototype with 1-3 core mechanics instead of a
      large framework or many levels.
    - Avoid verbose comments, repeated markup and long hard-coded data tables.
    - Do not use external URLs, CDNs, fetch, XMLHttpRequest, WebSocket, EventSource,
      eval, new Function, dynamic import, document.cookie, localStorage or sessionStorage.
    - index.html may only reference local styles.css and game.js.
    - Make the game clearly reflect the creatorIdea.
    - The result must be playable with keyboard and/or mouse and include visible
      objective, controls, progress, win state and lose/restart state.
    """
).strip()


def code_generation_agent(
    db: Session,
    task: GenerationTask,
    state: GenerationState,
) -> GenerationState:
    user_prompt = json.dumps(
        {
            "creatorIdea": state["idea_text"],
            "requirementProfile": state.get("requirement_profile", {}),
            "ideaBrief": state.get("idea_brief", {}),
            "assetContext": state.get("asset_context", []),
            "designDoc": state.get("design_doc", {}),
        },
        ensure_ascii=False,
    )
    bundle_json = generate_json(BUNDLE_SYSTEM_PROMPT, user_prompt)
    ensure_task_not_canceled(db, task)
    add_log(
        db,
        task,
        "code_generation_agent",
        "Generated structured static web game bundle with the configured LLM.",
        payload={
            "title": bundle_json.get("title"),
            "fileCount": len(bundle_json.get("files", [])),
        },
    )
    return {"bundle_json": bundle_json, "repair_attempts": 0}


def scan_bundle_security(bundle: GeneratedGameBundle) -> list[str]:
    errors: list[str] = []
    for file in bundle.files:
        for pattern, message in SECURITY_PATTERNS:
            if re.search(pattern, file.content, flags=re.IGNORECASE):
                errors.append(f"{file.path}: {message}")
    index = next(file for file in bundle.files if file.path == "index.html")
    if "game.js" in {file.path for file in bundle.files} and "game.js" not in index.content:
        errors.append("index.html must reference local game.js")
    if "styles.css" in {file.path for file in bundle.files} and "styles.css" not in index.content:
        errors.append("index.html must reference local styles.css")
    return errors


def bundle_security_scan(
    db: Session,
    task: GenerationTask,
    state: GenerationState,
) -> GenerationState:
    try:
        bundle = GeneratedGameBundle.model_validate(state.get("bundle_json"))
        errors = scan_bundle_security(bundle)
    except Exception as exc:  # noqa: BLE001
        errors = [f"{type(exc).__name__}: {exc}"]
        add_log(
            db,
            task,
            "bundle_security_scan",
            f"Generated bundle validation failed: {errors[0]}",
            AgentLogLevel.WARNING,
        )
        return {"security_errors": errors}

    if errors:
        add_log(
            db,
            task,
            "bundle_security_scan",
            f"Generated bundle failed security scan with {len(errors)} issue(s).",
            AgentLogLevel.WARNING,
            payload={"errors": errors},
        )
        return {"security_errors": errors}

    add_log(
        db,
        task,
        "bundle_security_scan",
        f"Validated static bundle with {len(bundle.files)} file(s).",
        payload=bundle.metadata_json(),
    )
    return {"bundle": bundle, "security_errors": []}


REPAIR_BUNDLE_SYSTEM_PROMPT = dedent(
    """
    Repair an invalid generated-game-bundle-v1 JSON object. Return JSON only.
    Preserve the user's game idea and gameplay intent, but fix every validation
    and security error. Do not use external URLs, network APIs, browser storage,
    eval, dynamic import, iframe, object or embed.
    """
).strip()


def repair_bundle(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    attempts = state.get("repair_attempts", 0) + 1
    user_prompt = json.dumps(
        {
            "creatorIdea": state["idea_text"],
            "invalidBundle": state.get("bundle_json"),
            "securityErrors": state.get("security_errors", []),
            "designDoc": state.get("design_doc", {}),
        },
        ensure_ascii=False,
    )
    repaired = generate_json(REPAIR_BUNDLE_SYSTEM_PROMPT, user_prompt)
    ensure_task_not_canceled(db, task)
    add_log(
        db,
        task,
        "repair_bundle",
        f"Repaired generated bundle JSON, attempt {attempts}.",
        payload={"attempt": attempts},
    )
    return {"bundle_json": repaired, "repair_attempts": attempts}


def upload_node(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.UPLOAD)
    ensure_task_not_canceled(db, task)
    user = db.get(User, state["user_id"])
    if not user:
        raise RuntimeError("User not found")

    bundle = state["bundle"]
    game = Game(
        owner_user_id=user.id,
        title=bundle.title,
        description=bundle.description,
        cover_url=None,
        status=str(GameStatus.DRAFT),
        tags=bundle.tags,
    )
    db.add(game)
    db.flush()
    task.result_game_id = game.id
    db.commit()

    version = GameVersion(
        game_id=game.id,
        generation_task_id=task.id,
        version_number=1,
        game_spec_json=bundle.metadata_json(),
        manifest_url=PENDING_STORAGE_VALUE,
        bundle_url=PENDING_STORAGE_VALUE,
        storage_prefix=PENDING_STORAGE_VALUE,
    )
    db.add(version)
    db.flush()

    prefix = f"games/{game.id}/versions/{version.id}"
    for file in bundle.files:
        ensure_task_not_canceled(db, task)
        upload_text_object(f"{prefix}/{file.path}", file.content, file.contentType)

    ensure_task_not_canceled(db, task)
    manifest = GameManifest(
        gameId=game.id,
        versionId=version.id,
        title=bundle.title,
        entry="index.html",
        entryUrl=public_object_url(f"{prefix}/index.html"),
        assets=[
            ManifestAsset(
                name=file.path,
                url=public_object_url(f"{prefix}/{file.path}"),
                contentType=file.contentType,
            )
            for file in bundle.files
            if file.path != "index.html"
        ],
        permissions=ManifestPermissions(network=False, storage=False),
    )
    manifest_url = upload_text_object(
        f"{prefix}/manifest.json",
        manifest.model_dump_json(),
        "application/json",
    )

    version.storage_prefix = prefix
    version.manifest_url = manifest_url
    version.bundle_url = manifest.entryUrl
    game.current_version_id = version.id
    task.result_manifest_url = manifest_url
    db.commit()
    add_log(db, task, "uploader", f"Uploaded generated bundle to MinIO prefix: {prefix}.")
    return {"game_id": game.id, "version_id": version.id, "manifest_url": manifest_url}


def finalizer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    ensure_task_not_canceled(db, task)
    task.status = str(TaskStatus.SUCCEEDED)
    task.current_step = str(TaskStep.READY)
    task.finished_at = datetime.now(UTC)
    db.commit()
    add_log(db, task, "finalizer", "Preview is ready. Publish when you are happy with the result.")
    return {}
