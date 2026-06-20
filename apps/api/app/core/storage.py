import json
from io import BytesIO

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
        ensure_public_read_policy(client, settings.minio_bucket)
    except S3Error as exc:
        raise RuntimeError(f"MinIO bucket check failed: {exc}") from exc


def ensure_public_read_policy(client: Minio | None = None, bucket_name: str | None = None) -> None:
    settings = get_settings()
    client = client or get_minio_client()
    bucket_name = bucket_name or settings.minio_bucket
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }
    client.set_bucket_policy(bucket_name, json.dumps(policy))


def public_object_url(object_name: str) -> str:
    settings = get_settings()
    return f"{settings.minio_public_endpoint.rstrip('/')}/{settings.minio_bucket}/{object_name.lstrip('/')}"


def upload_text_object(object_name: str, content: str, content_type: str) -> str:
    settings = get_settings()
    data = content.encode("utf-8")
    get_minio_client().put_object(
        settings.minio_bucket,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return public_object_url(object_name)
