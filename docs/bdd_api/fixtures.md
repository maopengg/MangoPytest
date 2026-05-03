# Fixtures — 公共 Fixture 设计

## 职责

提供测试跨步骤共享的 pytest fixtures，与 step 定义分离。

## 设计思路

```
test 开始
  → mock_api_client (session) 登录并缓存 token
  → db_session (session) 数据库连接
  → api_response (function) 空 dict，等 step 填充
  → created_entity (function) 空 dict，等 step 填充
  → test 执行
  → teardown 关闭连接
```

## 目录结构

```
fixtures/
├── bdd.py        # BDD 公共 fixture（api_response, created_entity）
└── clients.py    # API 客户端 + 数据库会话
```

## 写法

### BDD 公共 Fixture（`fixtures/bdd.py`）

```python
import pytest

@pytest.fixture
def api_response():
    """步骤间传递 API 响应，初始为空，@when 步骤通过 target_fixture 填充"""
    return {}

@pytest.fixture
def created_entity():
    """步骤间传递创建的实体，初始为空，@given 步骤填充 id"""
    return {}
```

### API 客户端（`fixtures/clients.py`）

```python
@pytest.fixture(scope="session")
def mock_api_client():
    """Session 级别：登录一次，所有测试共享 token"""
    api = APIClient(base_url=settings.BASE_URL)
    resp = api.post("/auth/login", {"username": "testuser", "password": md5(pwd)})
    api.set_token(resp["data"]["token"])
    return api

@pytest.fixture
def api_client():
    """Function 级别：未认证客户端，用于登录测试"""
    return APIClient()
```

### 数据库会话（`fixtures/clients.py`）

```python
@pytest.fixture(scope="session")
def db_session():
    """Session 级别数据库连接"""
    session = config.SessionLocal()
    yield session
    session.close()
```

## 作用域选择

| scope | 何时用 |
|-------|--------|
| `session` | 登录客户端、DB 连接——创建一次，全局复用 |
| `function` | 响应容器、实体容器——每个测试新实例，互不干扰 |

## 新增 Fixture

1. 在 `fixtures/` 下新建 `.py` 文件
2. conftest 自动发现，无需手动注册
