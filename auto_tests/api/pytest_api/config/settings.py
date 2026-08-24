"""pytest_api 的 API 运行配置。"""

from pathlib import Path

from pydantic import ConfigDict

from core.api.config import APIRuntimeConfig
from core.utils.artifacts import artifact_path

CONFIG_DIR = Path(__file__).resolve().parent


class PytestApiMockConfig(APIRuntimeConfig):
    PROJECT_NAME: str = "Pytest Mango Mock API 自动化测试"
    ALLURE_REPORT_DIR: str = artifact_path("reports", "pytest_api", "allure")
    ALLURE_HISTORY_DIR: str = artifact_path("reports", "pytest_api", "history")
    LOG_DIR: str = artifact_path("temp", "logs", "pytest_api")


class DevConfig(PytestApiMockConfig):
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8003"
    DB_HOST: str = "localhost"
    DB_NAME: str = "mango_mock_dev"
    LOG_LEVEL: str = "DEBUG"
    MOCK_RETRY_TIMES: int = 1
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.dev", env_file_encoding="utf-8", extra="allow"
    )


class _RemoteConfig(PytestApiMockConfig):
    BASE_URL: str = "http://43.142.161.61:8003"
    DB_HOST: str = "43.142.161.61"
    DB_USER: str = "root"
    DB_PASSWORD: str = "mP123456&"
    DB_NAME: str = "mango_mock"


class TestConfig(_RemoteConfig):
    ENV: str = "test"
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.test", env_file_encoding="utf-8", extra="allow"
    )


class PreConfig(_RemoteConfig):
    ENV: str = "pre"
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.pre", env_file_encoding="utf-8", extra="allow"
    )


class ProdConfig(_RemoteConfig):
    ENV: str = "prod"
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.prod", env_file_encoding="utf-8", extra="allow"
    )
