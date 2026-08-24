"""API 自动化项目共用的运行配置字段。"""

from pydantic import ConfigDict, Field

from core.base.config import BaseConfig


class APIRuntimeConfig(BaseConfig):
    """只描述 API 测试运行参数，不在配置加载阶段创建数据库连接。"""

    PROJECT_NAME: str
    MOCK_API_PREFIX: str = Field(default="/api", description="API 前缀")
    MOCK_TIMEOUT: int = Field(default=30, description="请求超时时间（秒）")
    MOCK_RETRY_TIMES: int = Field(default=3, description="请求重试次数")
    MOCK_ADMIN_TOKEN: str = Field(
        default="mango-mock-admin-20260725",
        description="用于清理隔离 Test Run 的 Mango Mock 管理令牌",
    )
    TEST_USERNAME: str = Field(default="testuser", description="测试用户名")
    TEST_PASSWORD: str = Field(
        default="482c811da5d5b4bc6d497ffa98491e38",
        description="测试密码（MD5）",
    )
    ALLURE_REPORT_DIR: str
    ALLURE_HISTORY_DIR: str
    LOG_DIR: str
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file_encoding="utf-8", extra="allow")
