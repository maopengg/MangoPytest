# Config — 多环境配置设计

## 职责

根据 `ENV` 环境变量加载对应环境的配置。UI 项目除了 API/浏览器配置外，还需要数据库连接来管理测试数据。

## 设计思路

```
os.environ["ENV"] = "prod"
    ↓
_resolve_env() → "prod"
    ↓
_config_mapping["prod"] → ProdConfig()
    ↓
settings.BASE_URL     → 被测页面地址
settings.SessionLocal → 数据库会话工厂
```

## 文件结构

```
config/
├── __init__.py       # _resolve_env() + get_config() + 全局 settings
├── settings.py       # 配置类 + SQLAlchemy 初始化
├── .env.dev
├── .env.test
├── .env.pre
└── .env.prod
```

## 写法

### 基础配置类（含数据库初始化）

```python
class BddUIMockConfig(BaseConfig):
    # 浏览器配置
    BROWSER: str = "chrome"
    HEADLESS: bool = False
    WINDOW_WIDTH: int = 1920

    # SQLAlchemy 延迟初始化
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DB_HOST and self.DB_NAME:
            db_url = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            self._engine = create_engine(db_url, poolclass=StaticPool, pool_pre_ping=True)
            self._SessionLocal = sessionmaker(bind=self._engine)
            self._Base = declarative_base()

    @property
    def SessionLocal(self):
        return self._SessionLocal

    @property
    def Base(self):
        return self._Base
```

### 环境配置

```python
class DevConfig(BddUIMockConfig):
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8003"
    HEADLESS: bool = False

class ProdConfig(BddUIMockConfig):
    ENV: str = "prod"
    BASE_URL: str = "http://your-server:8003"
    HEADLESS: bool = True
```

### 环境解析

```python
# __init__.py
_config_mapping = {"dev": DevConfig, "test": TestConfig, "pre": PreConfig, "prod": ProdConfig}

def _resolve_env() -> str:
    env = os.getenv("ENV")
    if env:
        return env.lower()
    from auto_tests.<project> import DEFAULT_ENV
    return DEFAULT_ENV.name.lower()

settings = get_config()
```

## .env 文件

```ini
# .env.prod
BASE_URL=http://your-server:8003
DB_HOST=your-server
DB_PORT=3306
DB_USER=root
DB_PASSWORD=xxx
DB_NAME=your_db
HEADLESS=true
```
