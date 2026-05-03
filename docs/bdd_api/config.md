# Config — 多环境配置设计

## 职责

根据 `ENV` 环境变量自动加载对应环境的配置（BASE_URL、数据库连接、密钥等），不硬编码任何环境值。

## 设计思路

```
os.environ["ENV"] = "prod"
    ↓
_resolve_env() → "prod"
    ↓
_config_mapping["prod"] → ProdConfig()
    ↓
settings = ProdConfig()   # 全局单例，项目各处直接 import
```

## 文件结构

```
config/
├── __init__.py       # _resolve_env() + get_config() + 全局 settings
├── settings.py       # 配置类定义（Base → Dev/Test/Pre/Prod）
├── .env.dev          # 各环境的敏感值（不入 git）
├── .env.test
├── .env.pre
└── .env.prod
```

## 写法

### 1. 基础配置类

```python
# settings.py
from pydantic import Field
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    model_config = {"env_file": ".env", "extra": "allow"}

    ENV: str = "test"
    BASE_URL: str = "http://localhost:8000"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "test"
```

### 2. 各环境配置类

```python
class DevConfig(BaseConfig):
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8003"

class ProdConfig(BaseConfig):
    ENV: str = "prod"
    BASE_URL: str = "http://your-server:8003"
```

### 3. 环境解析

```python
# __init__.py
import os

_config_mapping = {
    "dev": DevConfig, "test": TestConfig,
    "pre": PreConfig, "prod": ProdConfig,
}

def _resolve_env() -> str:
    env = os.getenv("ENV")
    if env:
        return env.lower()
    from auto_tests.<project> import DEFAULT_ENV
    return DEFAULT_ENV.name.lower()

def get_config(env=None):
    if env is None:
        env = _resolve_env()
    return _config_mapping[env]()

# 全局实例
settings = get_config()
```

### 4. .env 文件

```
# .env.prod
BASE_URL=http://your-server:8003
DB_HOST=your-server
DB_USER=root
DB_PASSWORD=xxx
DB_NAME=your_db
```

## 使用方式

项目任意位置直接导入全局 `settings`：

```python
from auto_tests.<project>.config import settings

client = APIClient(base_url=settings.BASE_URL)
session = settings.SessionLocal()
```

## 环境枚举对齐

`DEFAULT_ENV.name.lower()` 必须和 `_config_mapping` 的 key 一致。如 `EnvironmentEnum.PROD` → `"prod"` → `ProdConfig`。

## 注意事项

- `model_config["env_file"]` 指向 `.env`，子类可以覆盖为 `.env.prod` 等
- `extra="allow"` 允许子类添加额外字段
