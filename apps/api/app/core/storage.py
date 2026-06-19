from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


def get_minio_client() -> Minio:
    settings = get_settings()
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket() -> None:
    settings = get_settings()
    client = get_minio_client()
    try:
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
    except S3Error as exc:
        raise RuntimeError(f"MinIO bucket check failed: {exc}") from exc


def public_object_url(object_name: str) -> str:
    settings = get_settings()
    return f"{settings.minio_public_endpoint.rstrip('/')}/{settings.minio_bucket}/{object_name.lstrip('/')}"
