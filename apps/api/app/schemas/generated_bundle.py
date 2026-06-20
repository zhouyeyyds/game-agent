from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, Field, model_validator

ALLOWED_FILE_TYPES = {
    "index.html": "text/html",
    "game.js": "application/javascript",
    "styles.css": "text/css",
}
MAX_FILE_BYTES = 220_000
MAX_TOTAL_BYTES = 1_000_000


class BundlePermissions(BaseModel):
    network: bool = False
    storage: bool = False
    externalScripts: bool = False

    @model_validator(mode="after")
    def validate_locked_down(self) -> "BundlePermissions":
        if self.network or self.storage or self.externalScripts:
            raise ValueError(
                "bundle permissions must disable network, storage and external scripts"
            )
        return self


class BundleFile(BaseModel):
    path: str = Field(min_length=1, max_length=160)
    contentType: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_file(self) -> "BundleFile":
        validate_bundle_path(self.path, self.contentType)
        if len(self.content.encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError(f"file too large: {self.path}")
        return self


class GeneratedGameBundle(BaseModel):
    schemaVersion: Literal["generated-game-bundle-v1"] = "generated-game-bundle-v1"
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1200)
    tags: list[str] = Field(default_factory=list, max_length=12)
    entry: Literal["index.html"] = "index.html"
    files: list[BundleFile] = Field(min_length=1, max_length=12)
    permissions: BundlePermissions = Field(default_factory=BundlePermissions)

    @model_validator(mode="after")
    def validate_bundle(self) -> "GeneratedGameBundle":
        paths = [file.path for file in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("bundle file paths must be unique")
        if "index.html" not in paths:
            raise ValueError("bundle must include index.html")
        total_bytes = sum(len(file.content.encode("utf-8")) for file in self.files)
        if total_bytes > MAX_TOTAL_BYTES:
            raise ValueError("bundle is too large")
        return self

    def metadata_json(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "entry": self.entry,
            "files": [
                {
                    "path": file.path,
                    "contentType": file.contentType,
                    "sizeBytes": len(file.content.encode("utf-8")),
                }
                for file in self.files
            ],
            "permissions": self.permissions.model_dump(),
        }


class GeneratedBundleMetadataFile(BaseModel):
    path: str = Field(min_length=1, max_length=160)
    contentType: str = Field(min_length=1, max_length=120)
    sizeBytes: int = Field(ge=0, le=MAX_FILE_BYTES)

    @model_validator(mode="after")
    def validate_file(self) -> "GeneratedBundleMetadataFile":
        validate_bundle_path(self.path, self.contentType)
        return self


class GeneratedGameBundleMetadata(BaseModel):
    schemaVersion: Literal["generated-game-bundle-v1"] = "generated-game-bundle-v1"
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1200)
    tags: list[str] = Field(default_factory=list, max_length=12)
    entry: Literal["index.html"] = "index.html"
    files: list[GeneratedBundleMetadataFile] = Field(min_length=1, max_length=12)
    permissions: BundlePermissions = Field(default_factory=BundlePermissions)

    @model_validator(mode="after")
    def validate_metadata(self) -> "GeneratedGameBundleMetadata":
        paths = [file.path for file in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("bundle file paths must be unique")
        if "index.html" not in paths:
            raise ValueError("bundle must include index.html")
        total_bytes = sum(file.sizeBytes for file in self.files)
        if total_bytes > MAX_TOTAL_BYTES:
            raise ValueError("bundle is too large")
        return self


def validate_bundle_path(path: str, content_type: str) -> None:
    normalized = path.replace("\\", "/")
    parsed = PurePosixPath(normalized)
    if normalized != path:
        raise ValueError(f"backslash path is not allowed: {path}")
    if parsed.is_absolute():
        raise ValueError(f"absolute path is not allowed: {path}")
    if ".." in parsed.parts:
        raise ValueError(f"parent path is not allowed: {path}")
    if any(part.startswith(".") for part in parsed.parts):
        raise ValueError(f"hidden path is not allowed: {path}")
    if len(parsed.parts) == 1:
        expected = ALLOWED_FILE_TYPES.get(path)
        if not expected:
            raise ValueError(f"file path is not allowed: {path}")
        if content_type != expected:
            raise ValueError(f"invalid content type for {path}: {content_type}")
        return
    if len(parsed.parts) == 2 and parsed.parts[0] == "data" and path.endswith(".json"):
        if content_type != "application/json":
            raise ValueError(f"invalid content type for {path}: {content_type}")
        return
    raise ValueError(f"file path is not allowed: {path}")
