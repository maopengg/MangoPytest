"""bdd_ui 的 UI 运行配置，不初始化数据库连接。"""

from pydantic import ConfigDict, Field

from core.base.config import BaseConfig
from core.utils.artifacts import artifact_path


class BddUIMockConfig(BaseConfig):
    PROJECT_NAME: str = "BDD Mango Mock UI 自动化"
    BROWSER: str = "chromium"
    HEADLESS: bool = False
    IMPLICIT_WAIT: int = 10
    PAGE_LOAD_TIMEOUT: int = 30
    SCRIPT_TIMEOUT: int = 10
    WINDOW_WIDTH: int = 1440
    WINDOW_HEIGHT: int = 900
    TRACE_ENABLED: bool = True
    ARTIFACT_DIR: str = artifact_path("reports", "bdd_ui", "artifacts")
    ALLURE_REPORT_DIR: str = artifact_path("reports", "bdd_ui", "allure")
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file_encoding="utf-8", extra="allow")


class DevConfig(BddUIMockConfig):
    ENV: str = "dev"
    BASE_URL: str = Field(default="http://localhost:8003")
    HEADLESS: bool = False
    LOG_LEVEL: str = "DEBUG"
    model_config = ConfigDict(
        env_file=".env.dev", env_file_encoding="utf-8", extra="allow"
    )


class ProdConfig(BddUIMockConfig):
    ENV: str = "prod"
    BASE_URL: str = Field(default="http://43.142.161.61:8003")
    HEADLESS: bool = True
    model_config = ConfigDict(
        env_file=".env.prod", env_file_encoding="utf-8", extra="allow"
    )


class TestConfig(ProdConfig):
    ENV: str = "test"
    model_config = ConfigDict(
        env_file=".env.test", env_file_encoding="utf-8", extra="allow"
    )


class PreConfig(ProdConfig):
    ENV: str = "pre"
    model_config = ConfigDict(
        env_file=".env.pre", env_file_encoding="utf-8", extra="allow"
    )
