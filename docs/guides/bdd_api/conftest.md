# Conftest — pytest 入口设计

## 职责

1. 注册所有 pytest-bdd 步骤模块和 fixture 模块
2. 注册 pytest-factoryboy 的 Spec（数据工厂 fixture）
3. 提供会话级数据清理钩子

## 设计思路

```
pytest 启动
  → pytest_plugins 列表加载步骤 + fixture 模块
  → pytest_sessionstart 清理残留测试数据
  → 测试执行
  → pytest_sessionfinish 释放清理锁
```

## 写法

### 1. 自动发现模块

不手写 `pytest_plugins` 列表，用 `_discover_modules()` 自动扫描目录：

```python
from pathlib import Path

CONFTEST_DIR = Path(__file__).parent

pytest_plugins = ["core.api.bdd_steps"]  # 核心步骤

def _discover_modules(rel_dir, pkg_name):
    """扫描 rel_dir 下所有 .py（除 __init__），注册为 pytest plugin"""
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

有新文件放到 `steps/` 或 `fixtures/` 目录下，自动生效，不需要改 conftest。

### 2. 注册数据工厂 Spec

```python
# pytest-factoryboy 的 @register 在 import 时生效
from auto_tests.<project>.data_factory.specs.user import user_spec      # noqa: F401
from auto_tests.<project>.data_factory.specs.product import product_spec  # noqa: F401
```

新增 Spec 时在这里加一行 import。

### 3. 会话级数据清理

```python
def pytest_sessionstart(session):
    """测试开始前，清理上次残留的 AUTO_ 数据"""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()

def pytest_sessionfinish(session, exitstatus):
    """测试结束后释放清理锁"""
```

**清理锁机制**：用文件锁确保 `-n 3` 并行时只有一个 worker 执行清理，避免重复删除。

### 4. 日志配置

```python
def pytest_configure(config):
    import logging
    for name in ["core", "auto_tests", "mangotools"]:
        logging.getLogger(name).propagate = False

    config.addinivalue_line("markers", "smoke: 冒烟测试")
```

## pytest.ini

```ini
[pytest]
python_files = test_*.py
testpaths = test_cases
markers =
    smoke: 冒烟测试
    positive: 正向测试
    negative: 负向测试
    integration: 集成测试
addopts = -v --tb=short --strict-markers
```
