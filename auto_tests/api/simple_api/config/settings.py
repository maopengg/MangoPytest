"""simple_api 的 API 运行配置。"""

from pathlib import Path

from pydantic import ConfigDict

from core.api.config import APIRuntimeConfig
from core.utils.artifacts import artifact_path

CONFIG_DIR = Path(__file__).resolve().parent


class ApiMockConfig(APIRuntimeConfig):
    PROJECT_NAME: str = "Mango Mock API 轻量自动化测试"
    ALLURE_REPORT_DIR: str = artifact_path("reports", "simple_api", "allure")
    ALLURE_HISTORY_DIR: str = artifact_path("reports", "simple_api", "history")
    LOG_DIR: str = artifact_path("temp", "logs", "simple_api")


class DevConfig(ApiMockConfig):
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8003"
    LOG_LEVEL: str = "DEBUG"
    MOCK_RETRY_TIMES: int = 1
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.dev", env_file_encoding="utf-8", extra="allow"
    )


class _RemoteConfig(ApiMockConfig):
    BASE_URL: str = "http://43.142.161.61:8003"


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
