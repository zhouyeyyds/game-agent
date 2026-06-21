from app.core.config import Settings


def test_vm_host_builds_service_defaults() -> None:
    settings = Settings(_env_file=None, vm_host="10.0.0.5")

    assert settings.mysql_host == "10.0.0.5"
    assert (
        settings.database_url
        == "mysql+pymysql://game_agent:game_agent_password@10.0.0.5:13306/game_agent"
    )
    assert settings.minio_endpoint == "10.0.0.5:19000"
    assert settings.minio_public_endpoint == "http://10.0.0.5:19000"


def test_explicit_service_urls_override_vm_host_defaults() -> None:
    settings = Settings(
        _env_file=None,
        vm_host="10.0.0.5",
        database_url="mysql+pymysql://custom:secret@db.example.com:3306/custom",
        minio_endpoint="storage.example.com:9000",
        minio_public_endpoint="https://cdn.example.com",
    )

    assert settings.database_url == "mysql+pymysql://custom:secret@db.example.com:3306/custom"
    assert settings.minio_endpoint == "storage.example.com:9000"
    assert settings.minio_public_endpoint == "https://cdn.example.com"
