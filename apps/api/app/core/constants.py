from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskStep(StrEnum):
    QUEUED = "queued"
    IDEA = "idea"
    SPEC = "spec"
    RENDER = "render"
    UPLOAD = "upload"
    READY = "ready"
    PUBLISH = "publish"


class GameStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AgentLogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RuntimeType(StrEnum):
    IFRAME_MANIFEST_V1 = "iframe_manifest_v1"


class SchemaVersion(StrEnum):
    GAME_SPEC_V1 = "game-spec-v1"
    GAME_MANIFEST_V1 = "game-manifest-v1"


PENDING_STORAGE_VALUE = "pending"
