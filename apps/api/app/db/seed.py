from datetime import UTC, datetime

from sqlalchemy import select

from app.core.constants import GameStatus, PENDING_STORAGE_VALUE
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.core.storage import ensure_bucket, public_object_url, upload_text_object
from app.models import Game, GameVersion, User
from app.schemas.manifest import GameManifest, ManifestAsset, ManifestPermissions


def build_demo_game(game_id: str, version_id: str, title: str, body: str, accent: str) -> tuple[str, str, str]:
    prefix = f"games/{game_id}/versions/1"
    entry_url = public_object_url(f"{prefix}/index.html")
    js_url = public_object_url(f"{prefix}/game.js")
    css_url = public_object_url(f"{prefix}/styles.css")

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>{title}</title>
  <link rel='stylesheet' href='{css_url}' />
</head>
<body>
  <main class='game-shell'>
    <p class='eyebrow'>Remote HTML5 Bundle</p>
    <h1>{title}</h1>
    <p>{body}</p>
    <button id='complete'>完成游戏</button>
  </main>
  <script src='{js_url}'></script>
</body>
</html>"""
    js = """window.parent?.postMessage({ type: 'game.ready' }, '*');
document.getElementById('complete')?.addEventListener('click', () => {
  window.parent?.postMessage({ type: 'game.completed', result: 'win', durationMs: 1000 }, '*');
});
window.addEventListener('message', (event) => {
  if (event.data?.type === 'game.restart') window.location.reload();
});
"""
    css = f"""html, body {{ margin: 0; min-height: 100%; font-family: Inter, system-ui, sans-serif; background: #10111f; color: white; }}
.game-shell {{ min-height: 100vh; display: grid; place-content: center; padding: 48px; text-align: center; background: radial-gradient(circle at top, {accent}55, transparent 45%); }}
h1 {{ font-size: clamp(2rem, 6vw, 5rem); margin: 0 0 16px; }}
p {{ max-width: 680px; color: #cbd5e1; line-height: 1.8; }}
.eyebrow {{ color: {accent}; text-transform: uppercase; letter-spacing: .3em; font-size: 12px; }}
button {{ margin-top: 24px; border: 0; border-radius: 999px; padding: 14px 24px; background: {accent}; color: #080a12; font-weight: 700; cursor: pointer; }}
"""
    manifest = GameManifest(
        gameId=game_id,
        versionId=version_id,
        title=title,
        entry="index.html",
        entryUrl=entry_url,
        assets=[
            ManifestAsset(name="game.js", url=js_url, contentType="application/javascript"),
            ManifestAsset(name="styles.css", url=css_url, contentType="text/css"),
        ],
        permissions=ManifestPermissions(network=False, storage=False),
    )

    upload_text_object(f"{prefix}/index.html", html, "text/html")
    upload_text_object(f"{prefix}/game.js", js, "application/javascript")
    upload_text_object(f"{prefix}/styles.css", css, "text/css")
    manifest_url = upload_text_object(f"{prefix}/manifest.json", manifest.model_dump_json(), "application/json")
    return prefix, manifest_url, entry_url


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_bucket()

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "demo@example.com"))
        if not user:
            user = User(
                email="demo@example.com",
                password_hash=hash_password("password123"),
                display_name="Demo Creator",
            )
            db.add(user)
            db.flush()

        demos = [
            ("Neon Robot Mystery", "在霓虹雨夜中寻找失踪机器人的短篇互动冒险。", ["story", "sci-fi"], "#65e4ff"),
            ("Forest Rune Quest", "探索魔法森林，选择路线并解开古老符文。", ["fantasy", "choice"], "#a7f3d0"),
        ]

        for title, description, tags, accent in demos:
            existing = db.scalar(select(Game).where(Game.title == title))
            if existing:
                continue

            game = Game(
                owner_user_id=user.id,
                title=title,
                description=description,
                cover_url=None,
                status=str(GameStatus.PUBLISHED),
                tags=tags,
                published_at=datetime.now(UTC),
            )
            db.add(game)
            db.flush()

            version = GameVersion(
                game_id=game.id,
                version_number=1,
                manifest_url=PENDING_STORAGE_VALUE,
                bundle_url=PENDING_STORAGE_VALUE,
                storage_prefix=PENDING_STORAGE_VALUE,
            )
            db.add(version)
            db.flush()

            prefix, manifest_url, entry_url = build_demo_game(game.id, version.id, title, description, accent)
            version.storage_prefix = prefix
            version.manifest_url = manifest_url
            version.bundle_url = entry_url
            game.current_version_id = version.id

        db.commit()


if __name__ == "__main__":
    seed()
