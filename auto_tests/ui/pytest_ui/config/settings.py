"""pytest_ui 的 UI 运行配置，不初始化数据库连接。"""

from pathlib import Path

from pydantic import ConfigDict, Field

from core.ui.config import UIRuntimeConfig
from core.utils.artifacts import artifact_path

CONFIG_DIR = Path(__file__).resolve().parent


class PytestUIMockConfig(UIRuntimeConfig):
    PROJECT_NAME: str = "pytest Mango Mock UI 自动化"
    ELEMENT_PROJECT: str = "mock_ui"
    ELEMENT_PRODUCT: str = "MockUI服务"
    ARTIFACT_DIR: str = artifact_path("reports", "pytest_ui", "artifacts")
    ALLURE_REPORT_DIR: str = artifact_path("reports", "pytest_ui", "allure")
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file_encoding="utf-8", extra="allow")


class DevConfig(PytestUIMockConfig):
    ENV: str = "dev"
    BASE_URL: str = Field(default="http://localhost:8003")
    HEADLESS: bool = False
    LOG_LEVEL: str = "DEBUG"
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.dev", env_file_encoding="utf-8", extra="allow"
    )


class _RemoteConfig(PytestUIMockConfig):
    BASE_URL: str = Field(default="http://43.142.161.61:8003")
    HEADLESS: bool = True


class ProdConfig(_RemoteConfig):
    ENV: str = "prod"
    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.prod", env_file_encoding="utf-8", extra="allow"
    )


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
