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

## 认证与请求头设计

### 设计原则

- **`api_client` 不负责登录**：仅创建客户端并设置默认请求头（Content-Type、Accept）
- **登录由 BDD 步骤触发**：`管理员已登录`、`用户"xxx"已登录` 等步骤执行实际登录
- **登录后自动设置认证头**：token 自动写入 `api_client.headers`，后续请求自动携带
- **支持用户切换**：不同角色登录时更新同一个 `api_client` 的 Authorization 头

### 请求头叠加规则

优先级从低到高：

```
api_client.headers（默认 Content-Type / Accept）
    ↓ 登录步骤自动注入
+ Authorization: Bearer <token>
    ↓ BDD "设置请求头:" 步骤
+ custom_headers（覆盖同名 key，追加不同名 key）
    ↓ 单次请求参数
+ request() 的 headers 参数（最高优先级）
```

### 使用方式

**默认场景（管理员）**：
```
假如 管理员已登录           # 自动登录 testuser，设置 Authorization
当 POST "/orders":         # 请求自动携带 token
```

**切换用户**：
```
假如 部门经理已登录         # 自动登录 dept_manager，更新 Authorization
当 POST "/approvals":      # 请求使用新 token
```

**追加自定义请求头**：
```
假如 管理员已登录
假如 设置请求头:            # 在已有 Authorization 基础上追加
  | 字段名 | 值 |
  | X-Sign | abc123 |
```

### 缓存机制

同一用户多次登录时，第二次直接从缓存取 token，避免重复请求登录接口。

---

## 新增 Fixture

1. 在 `fixtures/` 下新建 `.py` 文件
2. conftest 自动发现，无需手动注册
