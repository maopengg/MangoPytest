"""所有同步 UI 自动化项目共用的运行配置。"""

from typing import Literal

from pydantic import ConfigDict, Field

from core.base.config import BaseConfig


class UIRuntimeConfig(BaseConfig):
    ELEMENT_SOURCE: Literal["excel", "feishu"] = Field(
        default="excel", description="UI 元素来源"
    )
    ELEMENT_PROJECT: str
    ELEMENT_PRODUCT: str

    BROWSER: str = Field(default="chromium", description="浏览器类型")
    BROWSER_PATH: str = Field(default="", description="浏览器可执行文件路径")
    HEADLESS: bool = Field(default=False, description="是否无头模式")
    IMPLICIT_WAIT: int = Field(default=10, description="隐式等待时间(秒)")
    PAGE_LOAD_TIMEOUT: int = Field(default=30, description="页面加载超时(秒)")
    SCRIPT_TIMEOUT: int = Field(default=10, description="脚本超时(秒)")
    WINDOW_WIDTH: int = Field(default=1440, description="窗口宽度")
    WINDOW_HEIGHT: int = Field(default=900, description="窗口高度")
    TRACE_ENABLED: bool = Field(default=True, description="采集 Playwright Trace")

    ELEMENT_HEALING_ENABLED: bool = Field(default=True, description="启用元素自愈")
    ELEMENT_HEALING_MODE: int = Field(default=2, description="元素自愈模式")
    AI_ELEMENT_HEALING_ENABLED: bool = Field(default=False, description="启用 AI 元素修复")
    AI_API_KEY: str = Field(default="", description="AI 模型 API Key")
    AI_BASE_URL: str = Field(
        default="https://api.siliconflow.cn/v1",
        description="AI 模型地址",
    )
    AI_MODEL: str = Field(
        default="THUDM/GLM-Z1-9B-0414",
        description="AI 模型名称",
    )

    ARTIFACT_DIR: str

    model_config = ConfigDict(env_file_encoding="utf-8", extra="allow")
