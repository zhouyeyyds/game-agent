from __future__ import annotations

import json
from datetime import UTC, datetime
from html import escape
from textwrap import dedent
from typing import Any

from sqlalchemy.orm import Session

from app.agents.llm import LLMConfigurationError, generate_json
from app.agents.state import GenerationState
from app.core.config import get_settings
from app.core.constants import (
    PENDING_STORAGE_VALUE,
    AgentLogLevel,
    GameStatus,
    TaskStatus,
    TaskStep,
)
from app.core.storage import public_object_url, upload_text_object
from app.models import AgentLog, Asset, Game, GameVersion, GenerationTask, User
from app.schemas.game_spec import ChoiceSpec, EndingSpec, GameSpec, SceneSpec, ThemeSpec
from app.schemas.manifest import GameManifest, ManifestAsset, ManifestPermissions


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
    task.status = str(status)
    task.current_step = str(step)
    if not task.started_at:
        task.started_at = datetime.now(UTC)
    db.commit()
    db.refresh(task)


def title_from_prompt(prompt: str) -> str:
    cleaned = " ".join(prompt.strip().split())
    if not cleaned:
        return "Untitled AI Adventure"
    if len(cleaned) <= 28:
        return cleaned
    words = cleaned[:28].split()
    return f"{' '.join(words[:-1] or words)}..."


def build_mock_spec(prompt: str) -> GameSpec:
    title = title_from_prompt(prompt)
    description = f"An AI-generated interactive story inspired by: {prompt[:140]}"
    return GameSpec(
        template="choice_adventure",
        title=title,
        description=description,
        tags=["ai-generated", "choice", "story"],
        theme=ThemeSpec(background="#10111f", primary="#65e4ff", accent="#ff4fd8"),
        startSceneId="scene_intro",
        scenes=[
            SceneSpec(
                id="scene_intro",
                title="The First Spark",
                body=f"Your idea becomes playable energy: {prompt[:220]}",
                choices=[
                    ChoiceSpec(label="Follow the glowing path", nextSceneId="scene_discovery"),
                    ChoiceSpec(label="Open the mysterious console", nextSceneId="scene_console"),
                ],
            ),
            SceneSpec(
                id="scene_discovery",
                title="Discovery Run",
                body=(
                    "You move through a world assembled by agents. "
                    "Every choice reshapes the game draft."
                ),
                choices=[ChoiceSpec(label="Finish the prototype", nextSceneId="ending_win")],
            ),
            SceneSpec(
                id="scene_console",
                title="Agent Console",
                body=(
                    "The console displays a validated GameSpec, a manifest, "
                    "and a remote bundle ready for upload."
                ),
                choices=[ChoiceSpec(label="Publish the build", nextSceneId="ending_win")],
            ),
        ],
        endings=[
            EndingSpec(
                id="ending_win",
                title="Prototype Published",
                body=(
                    "The generated game is ready to preview, publish, "
                    "and play from the arcade gallery."
                ),
                result="win",
            )
        ],
    )


def render_bundle(spec: GameSpec) -> dict[str, str]:
    spec_json = spec.model_dump_json().replace("<", "\\u003c")
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(spec.title)}</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <main class="game-shell">
    <section class="card">
      <p class="eyebrow">PromptPlay Generated</p>
      <h1 id="scene-title"></h1>
      <p id="scene-body"></p>
      <div id="choices" class="choices"></div>
    </section>
  </main>
  <script id="game-spec" type="application/json">{spec_json}</script>
  <script src="game.js"></script>
</body>
</html>"""
    js = """const spec = JSON.parse(document.getElementById('game-spec').textContent);
const scenes = new Map(spec.scenes.map((scene) => [scene.id, scene]));
const endings = new Map(spec.endings.map((ending) => [ending.id, ending]));
const titleEl = document.getElementById('scene-title');
const bodyEl = document.getElementById('scene-body');
const choicesEl = document.getElementById('choices');
let startedAt = Date.now();

function clearChoices() {
  while (choicesEl.firstChild) choicesEl.removeChild(choicesEl.firstChild);
}

function addButton(label, onClick) {
  const button = document.createElement('button');
  button.textContent = label;
  button.addEventListener('click', onClick);
  choicesEl.appendChild(button);
}

function renderScene(id) {
  const scene = scenes.get(id);
  const ending = endings.get(id);
  clearChoices();
  if (ending) {
    titleEl.textContent = ending.title;
    bodyEl.textContent = ending.body;
    addButton('Play again', restart);
    window.parent?.postMessage({
      type: 'game.completed',
      result: ending.result,
      endingId: ending.id,
      durationMs: Date.now() - startedAt
    }, '*');
    return;
  }
  if (!scene) {
    window.parent?.postMessage({ type: 'game.error', message: `Missing scene: ${id}` }, '*');
    return;
  }
  titleEl.textContent = scene.title;
  bodyEl.textContent = scene.body;
  scene.choices.forEach((choice) => addButton(choice.label, () => renderScene(choice.nextSceneId)));
}

function restart() {
  startedAt = Date.now();
  renderScene(spec.startSceneId);
}

window.addEventListener('message', (event) => {
  if (event.data?.type === 'game.restart') restart();
});

restart();
window.parent?.postMessage({ type: 'game.ready', manifestVersion: 'game-manifest-v1' }, '*');
"""
    css = "\n".join(
        [
            "html, body {",
            "  margin: 0;",
            "  min-height: 100%;",
            "  font-family: Inter, ui-sans-serif, system-ui, sans-serif;",
            f"  background: {spec.theme.background};",
            "  color: white;",
            "}",
            ".game-shell {",
            "  min-height: 100vh;",
            "  display: grid;",
            "  place-items: center;",
            "  padding: 32px;",
            "  background:",
            f"    radial-gradient(circle at top left, {spec.theme.primary}44, transparent 34%),",
            f"    radial-gradient(circle at bottom right, {spec.theme.accent}44, transparent 36%);",
            "}",
            ".card {",
            "  width: min(760px, 100%);",
            "  border: 1px solid rgba(255,255,255,.14);",
            "  border-radius: 32px;",
            "  padding: clamp(28px, 6vw, 56px);",
            "  background: rgba(5, 8, 20, .72);",
            "  box-shadow: 0 30px 90px rgba(0,0,0,.45);",
            "  backdrop-filter: blur(18px);",
            "}",
            ".eyebrow {",
            f"  color: {spec.theme.primary};",
            "  font-weight: 900;",
            "  text-transform: uppercase;",
            "  letter-spacing: .28em;",
            "  font-size: 12px;",
            "}",
            "h1 { margin: 12px 0 0; font-size: clamp(36px, 7vw, 76px); line-height: .95; }",
            "p { color: #cbd5e1; line-height: 1.8; font-size: 18px; }",
            ".choices { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }",
            "button {",
            "  border: 0;",
            "  border-radius: 999px;",
            "  padding: 14px 20px;",
            f"  background: linear-gradient(135deg, {spec.theme.primary}, {spec.theme.accent});",
            "  color: #05000b;",
            "  font-weight: 900;",
            "  cursor: pointer;",
            "}",
            "button:hover { transform: translateY(-1px); }",
        ]
    )
    return {
        "index.html": html,
        "game.js": js,
        "styles.css": css,
        "spec.json": json.dumps(spec.model_dump(), ensure_ascii=False, indent=2),
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
    idea = state["idea_text"]
    asset_context = load_asset_context(db, task)
    brief = {
        "coreIdea": idea[:500],
        "targetFormat": "choice_adventure",
        "requiredQualities": ["playable", "clear choices", "reachable ending", "safe text"],
    }
    add_log(
        db,
        task,
        "idea_analyzer",
        f"Analyzed creator prompt and found {len(asset_context)} uploaded asset reference(s).",
        payload={"brief": brief, "assets": asset_context},
    )
    return {"asset_context": asset_context, "idea_brief": brief}


def asset_interpreter(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    asset_context = state.get("asset_context", [])
    interpreted = [
        {
            **asset,
            "intendedUse": "reference material for theme, characters, or interaction details",
        }
        for asset in asset_context
    ]
    add_log(
        db,
        task,
        "asset_interpreter",
        f"Prepared {len(interpreted)} asset reference(s) for the design agent.",
        payload={"assets": interpreted},
    )
    return {"asset_context": interpreted}


def game_designer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.SPEC)
    design_doc = {
        "template": "choice_adventure",
        "sceneCountTarget": 4,
        "endingCountTarget": 2,
        "style": "interactive story with concise scenes and meaningful choices",
        "constraints": [
            "Use only safe plain text.",
            "Every choice must point to an existing scene or ending id.",
            "At least one ending must be reachable from the start scene.",
        ],
    }
    add_log(
        db,
        task,
        "game_designer",
        "Planned game structure, constraints, and validation targets.",
        payload=design_doc,
    )
    return {"design_doc": design_doc}


SPEC_SYSTEM_PROMPT = dedent(
    """
    You are a game design agent for a web game platform.
    Return only a JSON object matching game-spec-v1:
    - template must be "choice_adventure".
    - title and description must be concise plain text.
    - tags must be an array of short strings.
    - theme must contain background, primary, and accent hex colors.
    - startSceneId must point to an item in scenes.
    - scenes must contain id, title, body, and choices.
    - choices must contain label and nextSceneId.
    - endings must contain id, title, body, and result.

    Rules: ids must be unique, choices must target existing ids, no script/html/javascript
    URLs, and at least one ending must be reachable.
    """
).strip()


def spec_writer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    settings = get_settings()
    if settings.llm_provider == "mock":
        spec = build_mock_spec(state["idea_text"])
        add_log(db, task, "spec_writer", "Generated mock GameSpec because LLM_PROVIDER=mock.")
        return {"spec_json": spec.model_dump(), "repair_attempts": 0}

    user_prompt = json.dumps(
        {
            "creatorIdea": state["idea_text"],
            "ideaBrief": state.get("idea_brief", {}),
            "assetContext": state.get("asset_context", []),
            "designDoc": state.get("design_doc", {}),
        },
        ensure_ascii=False,
    )
    spec_json = generate_json(SPEC_SYSTEM_PROMPT, user_prompt)
    add_log(
        db,
        task,
        "spec_writer",
        "Generated GameSpec JSON with the configured OpenAI-compatible model.",
        payload={"model": settings.llm_model, "title": spec_json.get("title")},
    )
    return {"spec_json": spec_json, "repair_attempts": 0}


def spec_reviewer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    try:
        spec = GameSpec.model_validate(state.get("spec_json"))
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"
        add_log(
            db,
            task,
            "spec_reviewer",
            f"GameSpec validation failed: {error}",
            AgentLogLevel.WARNING,
        )
        return {"validation_errors": [error]}
    add_log(
        db,
        task,
        "spec_reviewer",
        f"Validated GameSpec with {len(spec.scenes)} scene(s) and {len(spec.endings)} ending(s).",
    )
    return {"spec": spec, "validation_errors": []}


REPAIR_SYSTEM_PROMPT = dedent(
    """
    You repair invalid GameSpec JSON. Return only one complete JSON object matching
    game-spec-v1. Preserve the creator's idea, fix all validation errors, and do not
    include markdown.
    """
).strip()


def repair_spec(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    attempts = state.get("repair_attempts", 0) + 1
    settings = get_settings()
    if settings.llm_provider == "mock":
        spec = build_mock_spec(state["idea_text"])
        add_log(
            db,
            task,
            "repair_spec",
            "Rebuilt mock GameSpec after validation failure.",
            payload={"attempt": attempts},
        )
        return {"spec_json": spec.model_dump(), "repair_attempts": attempts}

    user_prompt = json.dumps(
        {
            "creatorIdea": state["idea_text"],
            "invalidSpec": state.get("spec_json"),
            "validationErrors": state.get("validation_errors", []),
        },
        ensure_ascii=False,
    )
    try:
        repaired = generate_json(REPAIR_SYSTEM_PROMPT, user_prompt)
    except LLMConfigurationError:
        raise
    add_log(
        db,
        task,
        "repair_spec",
        f"Repaired GameSpec JSON, attempt {attempts}.",
        payload={"attempt": attempts},
    )
    return {"spec_json": repaired, "repair_attempts": attempts}


def render_node(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.RENDER)
    files = render_bundle(state["spec"])
    add_log(
        db,
        task,
        "renderer",
        "Rendered index.html, game.js, styles.css and spec.json from GameSpec.",
    )
    return {"files": files}


def upload_node(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    update_step(db, task, TaskStep.UPLOAD)
    user = db.get(User, state["user_id"])
    if not user:
        raise RuntimeError("User not found")

    spec = state["spec"]
    game = Game(
        owner_user_id=user.id,
        title=spec.title,
        description=spec.description,
        cover_url=None,
        status=str(GameStatus.DRAFT),
        tags=spec.tags,
    )
    db.add(game)
    db.flush()
    task.result_game_id = game.id
    db.commit()

    version = GameVersion(
        game_id=game.id,
        generation_task_id=task.id,
        version_number=1,
        game_spec_json=spec.model_dump(),
        manifest_url=PENDING_STORAGE_VALUE,
        bundle_url=PENDING_STORAGE_VALUE,
        storage_prefix=PENDING_STORAGE_VALUE,
    )
    db.add(version)
    db.flush()

    prefix = f"games/{game.id}/versions/{version.id}"
    files = state["files"]
    upload_text_object(f"{prefix}/index.html", files["index.html"], "text/html")
    upload_text_object(f"{prefix}/game.js", files["game.js"], "application/javascript")
    upload_text_object(f"{prefix}/styles.css", files["styles.css"], "text/css")
    upload_text_object(f"{prefix}/spec.json", files["spec.json"], "application/json")

    manifest = GameManifest(
        gameId=game.id,
        versionId=version.id,
        title=spec.title,
        entry="index.html",
        entryUrl=public_object_url(f"{prefix}/index.html"),
        assets=[
            ManifestAsset(
                name="game.js",
                url=public_object_url(f"{prefix}/game.js"),
                contentType="application/javascript",
            ),
            ManifestAsset(
                name="styles.css",
                url=public_object_url(f"{prefix}/styles.css"),
                contentType="text/css",
            ),
            ManifestAsset(
                name="spec.json",
                url=public_object_url(f"{prefix}/spec.json"),
                contentType="application/json",
            ),
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
    add_log(db, task, "uploader", f"Uploaded remote bundle to MinIO prefix: {prefix}.")
    return {"game_id": game.id, "version_id": version.id, "manifest_url": manifest_url}


def finalizer(db: Session, task: GenerationTask, state: GenerationState) -> GenerationState:
    task.status = str(TaskStatus.SUCCEEDED)
    task.current_step = str(TaskStep.READY)
    task.finished_at = datetime.now(UTC)
    db.commit()
    add_log(db, task, "finalizer", "Preview is ready. Publish when you are happy with the result.")
    return {}
