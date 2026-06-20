from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assets, auth, games, generation_tasks, health, telemetry
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.request_id import RequestIdMiddleware
from app.core.storage import ensure_bucket
from app.db.schema_upgrade import ensure_runtime_schema
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    ensure_bucket()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="PromptPlay AI API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api")
    app.include_router(games.router, prefix="/api")
    app.include_router(assets.router, prefix="/api")
    app.include_router(generation_tasks.router, prefix="/api")
    app.include_router(telemetry.router, prefix="/api")
    return app


app = create_app()
