# BDD API Mock - BDD 自动化测试框架

## 项目概述

本项目是一个基于 **pytest-bdd** 和 **pytest-factoryboy** 的 BDD（行为驱动开发）API 自动化测试框架，针对 Mango Mock API 服务进行测试。使用 **Gherkin** 语法编写测试用例，让业务人员、测试人员和开发人员使用统一的语言描述业务场景。

**核心特性**：

- **BDD 中文语法**：使用 Gherkin 中文编写，业务可读可写
- **pytest-factoryboy**：自动注册 fixtures，简化测试数据创建
- **数据库直连**：SQLAlchemy 直接操作数据库，快速准备测试数据
- **占位符变量**：`${entity.id}` 语法实现步骤间数据传递
- **自动清理**：Repository 模式自动清理测试数据
- **模块化步骤**：按功能分类的 steps 模块，便于维护

---

## 架构设计

### 五层架构

```
L5: Feature 文件（Gherkin 语法）
    ├── 中文描述业务场景
    ├── 假如存在"实体" - 准备测试数据
    ├── 当 GET/POST "接口" - 调用 API
    └── 那么 响应状态码应该为 200 - 验证结果
    ↓
L4: Steps 步骤定义层（按功能分类）
    ├── common/    - 通用 fixtures (api_response, created_entity)
    ├── api/       - API 调用步骤 (GET, POST, PUT, DELETE)
    ├── auth/      - 认证相关步骤 (登录、权限)
    ├── data/      - 数据准备步骤 (factory_boy 创建实体)
    └── assertions/ - 断言验证步骤 (状态码、数据字段)
    ↓
L3: Factories 数据工厂层（pytest-factoryboy）
    ├── 自动注册为 pytest fixtures
    ├── 自动创建关联实体（SubFactory）
    └── 派生字段计算（LazyAttribute）
    ↓
L2: Entities 实体层（SQLAlchemy）
    ├── ORM 映射数据库表
    ├── 关联关系定义（relationship）
    └── to_api_payload() 序列化方法
    ↓
L1: Repositories 数据访问层
    ├── 按业务域分包（auth/user/product/order/...）
    ├── CODE_FIELD 映射清理字段
    └── delete_by_pattern() 批量清理
```

### 数据流向

```
Feature 文件（Gherkin）
    ↓ 解析
Steps 步骤定义
    ↓ 调用
Factories（pytest-factoryboy）
    ↓ 创建
Entities（SQLAlchemy）
    ↓ 持久化
数据库（MySQL）
    ↓ API 调用
后端服务（Mock API）
```

---

## 目录结构

```
auto_tests/bdd_api_mock/
├── features/               # Feature 文件（Gherkin 语法）
│   ├── auth/               # 认证模块
│   │   ├── auth.feature
│   │   └── test_auth_bdd.py
│   ├── user/               # 用户模块
│   ├── product/            # 产品模块
│   ├── order/              # 订单模块
│   ├── data/               # 数据提交模块
│   ├── file/               # 文件模块
│   ├── reimbursement/      # 报销申请模块
│   ├── approval/           # 审批流程模块
│   └── system/             # 系统管理模块
│
├── steps/                  # 步骤定义层（按功能分类）
│   ├── __init__.py         # 导出所有步骤
│   ├── common/             # 通用 fixtures
│   │   └── __init__.py     # api_response, created_entity
│   ├── api/                # API 请求步骤
│   │   ├── __init__.py
│   │   ├── base.py         # GET, POST, PUT, DELETE
│   │   └── entity.py       # 带实体 ID 的请求
│   ├── auth/               # 认证步骤
│   │   ├── __init__.py
│   │   └── login.py        # 登录相关步骤
│   ├── data/               # 数据准备步骤
│   │   ├── __init__.py
│   │   └── factory.py      # factory_boy 创建实体
│   └── assertions/         # 断言步骤
│       ├── __init__.py
│       ├── response.py     # 状态码、消息断言
│       └── data.py         # 数据字段、列表、数据库断言
│
├── factories/              # 数据工厂层（pytest-factoryboy）
│   ├── __init__.py         # BaseFactory 基类
│   └── specs/              # factory_boy Spec 定义
│       ├── user/
│       ├── product/
│       ├── order/
│       ├── data/
│       ├── file/
│       ├── reimbursement/
│       └── approval/
│
├── entities/               # SQLAlchemy 实体层
│   ├── __init__.py
│   ├── user/
│   ├── product/
│   ├── order/
│   ├── data/
│   ├── file/
│   ├── reimbursement/
│   ├── approval/
│   └── system/
│
├── repos/                  # Repository 数据访问层
│   ├── __init__.py
│   ├── base.py             # BaseRepository 基类
│   ├── user/
│   ├── product/
│   ├── order/
│   ├── data/
│   ├── file/
│   ├── reimbursement/
│   ├── approval/
│   └── system/
│
├── hooks/                  # 测试钩子
│   ├── __init__.py
│   └── cleanup_hooks.py    # 数据清理钩子
│
├── config/                 # 配置管理
│   ├── __init__.py
│   └── settings.py         # MockAPISettings 配置类
│
├── api_client.py           # APIClient HTTP 客户端
├── conftest.py             # pytest 全局配置
└── README.md               # 本文档
```

---

## 核心模块功能说明

### 1. Features（Feature 文件）

**职责**：使用 Gherkin 语法描述业务场景，是测试的起点。

**核心特性**：
- 中文语法（`# language: zh-CN`）
- 支持占位符变量（`${entity.id}`）
- 步骤间数据传递

**示例**：

```gherkin
# language: zh-CN
功能: 用户管理
  作为系统管理员
  我希望能够管理用户
  以便维护系统用户数据

  背景:
    假如 管理员已登录

  @smoke @positive
  场景: 获取所有用户列表
    当 GET "/users"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表
```

### 2. Steps（步骤定义层 - 模块化分类）

**职责**：将 Gherkin 步骤映射到 Python 代码，按功能分类管理。

#### 2.1 common/ - 通用 Fixtures

```python
# steps/common/__init__.py
import pytest

@pytest.fixture
def api_response():
    """API 响应 fixture"""
    return {}

@pytest.fixture
def created_entity():
    """当前创建的实体 fixture"""
    return {}
```

#### 2.2 api/ - API 调用步骤

```python
# steps/api/base.py
@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"'))
def api_get_step(path: str, mock_api_client, api_response):
    """GET 请求步骤"""
    result = mock_api_client.get(path)
    api_response.clear()
    api_response.update(result)

# steps/api/entity.py
@when(parsers.re(r'使用(?P<entity_name>\w+)ID\s+GET\s+"(?P<path>[^"]+)"'))
def api_get_with_entity_step(
    entity_name: str, path: str, mock_api_client, created_entity, api_response
):
    """使用实体ID的 GET 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    result = mock_api_client.get(path, created_entity=entity)
    api_response.clear()
    api_response.update(result)
```

#### 2.3 data/ - 数据准备步骤

```python
# steps/data/factory.py
@given(parsers.parse('存在"{entity_name}"'))
def create_entity_step_simple(entity_name: str, created_entity: Dict):
    """创建实体步骤（无参数）"""
    factory_class = ENTITY_FACTORY_MAP.get(entity_name)
    entity = factory_class()
    _entity_cache[entity_name] = entity
    created_entity.clear()
    created_entity.update({
        "entity": entity,
        "id": getattr(entity, "id", None),
        "entity_name": entity_name,
    })
```

#### 2.4 assertions/ - 断言验证步骤

```python
# steps/assertions/response.py
@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_code_should_be_cn(expected_code: int, api_response: Dict[str, Any]):
    """验证响应状态码（中文）"""
    actual_code = api_response.get("code", api_response.get("status_code", 0))
    assert actual_code == expected_code

# steps/assertions/data.py
@then(parsers.parse('响应数据应该包含字段 "{field}"'))
def response_data_should_contain_field_cn(field: str, api_response: Dict[str, Any]):
    """验证响应数据包含字段（中文）"""
    data = api_response.get("data", {})
    assert field in data
```

### 3. Factories（数据工厂层 - pytest-factoryboy）

**职责**：使用 pytest-factoryboy 自动注册 fixtures，处理关联关系。

**核心特性**：
- `@register` 装饰器自动注册为 pytest fixture
- `SubFactory` 自动创建关联实体
- `LazyAttribute` 计算派生字段

**示例**：

```python
# factories/specs/order/order_spec.py
from pytest_factoryboy import register
from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.entities.order import OrderEntity
from auto_tests.bdd_api_mock.factories.specs.user import user_spec
from auto_tests.bdd_api_mock.factories.specs.product import product_spec


@register
class OrderSpec(BaseFactory):
    """订单 Spec"""
    class Meta:
        model = OrderEntity

    # 关联实体 - 自动创建
    user = factory.SubFactory(user_spec)
    product = factory.SubFactory(product_spec)

    # 外键字段
    user_id = factory.SelfAttribute("user.id")
    product_id = factory.SelfAttribute("product.id")
    quantity = factory.Faker("random_int", min=1, max=10)
    total_amount = factory.LazyAttribute(
        lambda o: o.quantity * o.product.price if o.product else 0
    )
```

### 4. Entities（实体层 - SQLAlchemy）

**职责**：ORM 映射数据库表，定义关联关系。

**示例**：

```python
# entities/user/user_entity.py
from sqlalchemy import Column, Integer, String
from auto_tests.bdd_api_mock.config import Base


class UserEntity(Base):
    """用户实体"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    status = Column(String(20), default="active")
```

### 5. Repositories（数据访问层）

**职责**：封装数据访问，支持自动清理。

**示例**：

```python
# repos/user/user_repo.py
from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.entities.user import UserEntity


class UserRepo(BaseRepository[UserEntity]):
    """用户 Repository"""
    model = UserEntity
    CODE_FIELD = "username"  # 用于模式匹配清理

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        stmt = select(UserEntity).where(UserEntity.username == username)
        return self.session.execute(stmt).scalar_one_or_none()
```

### 6. Hooks（钩子层）

**职责**：测试生命周期管理，自动清理数据。

```python
# hooks/cleanup_hooks.py
class TestDataCleaner:
    """测试数据清理器"""

    def __init__(self, session: Session):
        self.session = session
        self.repos = [
            UserRepo(session),
            ProductRepo(session),
            OrderRepo(session),
            # ...
        ]

    def clear_all(self):
        """清理所有 AUTO_ 开头的测试数据"""
        for repo in self.repos:
            if hasattr(repo, 'CODE_FIELD') and repo.CODE_FIELD:
                repo.delete_by_pattern("AUTO_%")
```

---

## 测试分层

| 层级 | 类型 | 占比 | 用途 |
|------|------|------|------|
| API | 单接口测试 | 60% | 验证本模块逻辑、边界、异常 |
| Integration | 模块集成测试 | 30% | 验证真实依赖（A→B→C→D） |
| E2E | 端到端测试 | 10% | 验证完整业务闭环 |

---

## 快速开始

### 1. 安装依赖

```bash
pip install pytest pytest-bdd pytest-factoryboy factory_boy sqlalchemy pymysql requests
```

### 2. 配置环境

编辑 `config/settings.py`：

```python
class MockAPISettings(BaseConfig):
    """Mock API 测试配置"""

    # API 基础 URL
    BASE_URL: str = "http://43.142.161.61:8003"

    # 数据库配置
    DB_HOST: str = "43.142.161.61"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "mP123456&"
    DB_NAME: str = "mango_mock"
```

### 3. 运行测试

```bash
# 运行所有测试
pytest auto_tests/bdd_api_mock/

# 运行特定模块
pytest auto_tests/bdd_api_mock/features/auth/

# 运行特定 feature
pytest auto_tests/bdd_api_mock/features/user/test_user_bdd.py

# 运行并显示日志
pytest auto_tests/bdd_api_mock/ -v -s --log-cli-level=INFO

# 按标签运行
pytest auto_tests/bdd_api_mock/ -m smoke
pytest auto_tests/bdd_api_mock/ -m integration
```

---

## 最佳实践

### 1. 使用占位符传递数据

```gherkin
# ✅ 正确：使用 ${entity.id} 引用之前创建的实体
假如 存在"用户"
当 使用用户ID GET "/users?id=${user.id}"

# ❌ 错误：硬编码 ID
当 GET "/users?id=123"
```

### 2. 使用 Factory 创建数据

```python
# ✅ 正确：使用 Factory 自动创建关联实体
# 在 feature 文件中
假如 存在"订单"  # 自动创建用户和产品

# ❌ 错误：手动创建所有关联实体
假如 存在"用户"
而且 存在"产品"
当 POST "/orders":
  """
  {"user_id": ${user.id}, "product_id": ${product.id}}
  """
```

### 3. 使用 Trait 定义特定状态

```python
# 在 Spec 中定义 Trait
class OrderSpec(BaseFactory):
    class Params:
        paid = factory.Trait(status="paid", paid_at=factory.Faker("date_time"))

# 在测试中使用（通过步骤定义）
假如 存在"已支付订单"  # 使用 Trait 创建特定状态
```

### 4. 模块化的步骤定义

```python
# ✅ 正确：按功能分类步骤
# steps/api/base.py - 基础 HTTP 请求
# steps/api/entity.py - 带实体 ID 的请求
# steps/auth/login.py - 登录相关
# steps/data/factory.py - 数据创建
# steps/assertions/response.py - 响应断言
# steps/assertions/data.py - 数据断言
```

---

## API 覆盖

### 已实现的 API 模块

| 模块 | API | 测试场景 |
|------|-----|----------|
| **auth** | POST /auth/login | 登录成功/失败 |
| **user** | GET/POST/PUT/DELETE /users | CRUD 操作 |
| **product** | GET/POST/PUT/DELETE /products | CRUD 操作 |
| **order** | GET/POST/PUT/DELETE /orders | CRUD 操作 |
| **data** | POST /api/data | 数据提交 |
| **file** | GET /info | 服务器信息 |
| **reimbursement** | GET/POST/PUT/DELETE /reimbursements | 报销申请 |
| **approval** | GET/POST /dept-approvals, /finance-approvals, /ceo-approvals | 三级审批 |
| **system** | GET /health, /info | 系统状态 |

---

## 数据库表

### 核心表

- **users** - 用户表
- **products** - 产品表
- **orders** - 订单表
- **data_submissions** - 数据提交表
- **files** - 文件上传表
- **reimbursements** - 报销申请表
- **dept_approvals** - 部门审批表（C级）
- **finance_approvals** - 财务审批表（B级）
- **ceo_approvals** - 总经理审批表（A级）
- **approval_logs** - 审批流程日志表
- **api_logs** - API调用日志表

---

## 参考

- [pytest-bdd 文档](https://pytest-bdd.readthedocs.io/)
- [pytest-factoryboy 文档](https://pytest-factoryboy.readthedocs.io/)
- [factory_boy 文档](https://factoryboy.readthedocs.io/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

---

## 项目特点

1. **模块化 Steps**：按功能分类（api/auth/data/assertions），便于维护
2. **pytest-factoryboy**：自动注册 fixtures，简化测试数据创建
3. **自动清理**：每个测试前自动清理 AUTO_ 开头的测试数据
4. **占位符支持**：`${entity.id}` 语法实现步骤间数据传递
5. **中文 Gherkin**：业务人员可读的测试用例
