from app.api.routes.assets import ALLOWED_CONTENT_TYPES, MAX_UPLOAD_BYTES


def test_upload_limits_allow_multimodal_assets_up_to_100mb() -> None:
    assert MAX_UPLOAD_BYTES == 100 * 1024 * 1024
    assert {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
        "video/mp4",
        "video/webm",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/json",
    }.issubset(ALLOWED_CONTENT_TYPES)
