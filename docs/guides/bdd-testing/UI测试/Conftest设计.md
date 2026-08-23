# Conftest — pytest 入口设计

## 职责

1. 自动发现并注册所有步骤模块和 fixture 模块
2. 提供数据库会话 fixture
3. 提供会话级数据清理钩子

## 设计思路

```
pytest 启动
  → _discover_modules("steps")    注册所有步骤
  → _discover_modules("fixtures") 注册所有 fixture
  → pytest_sessionstart           清理残留 AUTO_ 数据
  → 测试执行
  → pytest_sessionfinish          释放清理锁
```

## 写法

### 1. 自动发现模块

```python
from pathlib import Path

CONFTEST_DIR = Path(__file__).parent

pytest_plugins = ["core.api.bdd_steps"]

def _discover_modules(rel_dir, pkg_name):
    base = CONFTEST_DIR / rel_dir
    if not base.is_dir():
        return
    for pyfile in sorted(base.rglob("*.py")):
        if pyfile.name == "__init__.py":
            continue
        mod = f"{pkg_name}.{pyfile.relative_to(base).with_suffix('').as_posix().replace('/', '.')}"
        pytest_plugins.append(mod)

_discover_modules("steps", "auto_tests.<project>.steps")
_discover_modules("fixtures", "auto_tests.<project>.fixtures")
```

新增步骤或 fixture 文件后自动生效，无需手动注册。

### 2. 数据库会话

```python
@pytest.fixture(scope="session")
def db_session():
    config = get_config()
    if not config.SessionLocal:
        yield None
        return
    session = config.SessionLocal()
    yield session
    session.close()
```

`SessionLocal` 为 None 时（数据库未配置）优雅降级，不影响纯 UI 测试。

### 3. 数据清理钩子

```python
def pytest_sessionstart(session):
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()

def pytest_sessionfinish(session, exitstatus):
    # 释放清理锁文件
```

清理逻辑和锁机制与 BDD API 完全相同，详见 [hooks.md](hooks.md)。

### 4. 日志配置

```python
def pytest_configure(config):
    import logging
    for name in ["core", "auto_tests", "mangotools"]:
        logging.getLogger(name).propagate = False
```

阻止框架日志重复输出到 Allure 报告。
