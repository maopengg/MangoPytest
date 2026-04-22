# BDD API Mock - BDD 自动化测试框架

## 项目概述

本项目是一个基于 **pytest-bdd** 的 BDD（行为驱动开发）API 自动化测试框架，针对 Mango Mock API 服务进行测试。使用 **Gherkin** 语法编写测试用例，让业务人员、测试人员和开发人员使用统一的语言描述业务场景。

**核心特性**：

- **BDD 中文语法**：使用 Gherkin 中文编写，业务可读可写
- **数据工厂**：factory_boy 自动创建关联实体，无需手动处理依赖
- **数据库直连**：SQLAlchemy 直接操作数据库，快速准备测试数据
- **占位符变量**：`${entity.id}` 语法实现步骤间数据传递
- **自动清理**：Repository 模式自动清理测试数据

---

## 架构设计

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│  Feature 文件（Gherkin 语法）                              │
│  ├── 中文描述业务场景                                      │
│  ├── 假如存在"实体" - 准备测试数据                         │
│  ├── 当 GET/POST "接口" - 调用 API                        │
│  └── 那么 response code should be 200 - 验证结果          │
├─────────────────────────────────────────────────────────┤
│  Steps 步骤定义层                                          │
│  ├── data_steps.py - 数据准备步骤（使用 factory_boy）      │
│  ├── api_steps.py - API 调用步骤                          │
│  ├── assertion_steps.py - 断言验证步骤                     │
│  └── auth_steps.py - 认证相关步骤                          │
├─────────────────────────────────────────────────────────┤
│  Specs 数据工厂层（factory_boy）                           │
│  ├── 自动创建关联实体（SubFactory）                        │
│  ├── 派生字段计算（LazyAttribute）                         │
│  └── 默认值 + 覆盖机制                                     │
├─────────────────────────────────────────────────────────┤
│  Entities 实体层（SQLAlchemy）                             │
│  ├── ORM 映射数据库表                                      │
│  ├── 关联关系定义（relationship）                          │
│  └── to_api_payload() 序列化方法                           │
├─────────────────────────────────────────────────────────┤
│  Repository 数据访问层                                     │
│  ├── 按业务域分包（auth/user/product/order/...）           │
│  ├── CODE_FIELD 映射清理字段                               │
│  └── delete_by_pattern() 批量清理                          │
├─────────────────────────────────────────────────────────┤
│  Hooks 钩子层                                              │
│  └── cleanup_hooks.py - 测试后自动清理数据                 │
└─────────────────────────────────────────────────────────┘
```

### 数据流向

```
Feature 文件（Gherkin）
    ↓ 解析
Steps 步骤定义
    ↓ 调用
Specs 数据工厂（factory_boy）
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
├── steps/                  # 步骤定义层
│   ├── __init__.py
│   ├── data_steps.py       # 数据准备步骤
│   ├── api_steps.py        # API 调用步骤
│   ├── assertion_steps.py  # 断言验证步骤
│   └── auth_steps.py       # 认证相关步骤
│
├── factories/              # 数据工厂层
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
├── db/                     # 数据库配置
│   ├── __init__.py
│   └── base.py             # SQLAlchemy Base 和 Session
│
├── config/                 # 配置管理
│   └── settings.py
│
└── conftest.py             # pytest 全局配置
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

### 2. Steps（步骤定义层）

**职责**：将 Gherkin 步骤映射到 Python 代码。

#### 2.1 data_steps.py - 数据准备

```python
@given(parsers.parse('存在"{entity_name}":'), target_fixture="created_entity")
def create_entity_step(entity_name: str, docstring):
    """创建实体步骤"""
    factory_class = ENTITY_FACTORY_MAP.get(entity_name)
    overrides = json.loads(docstring) if docstring else {}
    entity = factory_class(**overrides)
    return entity
```

#### 2.2 api_steps.py - API 调用

```python
@when(parsers.re(r'GET "(?P<path>[^"]+)"'), target_fixture="api_response")
def api_get_step(path: str, api_client: APIClient, created_entity=None):
    """GET 请求步骤"""
    return api_client.get(path, created_entity)
```

#### 2.3 assertion_steps.py - 断言验证

```python
@then(parsers.parse('响应状态码应该为 {expected_code:d}'))
def response_code_should_be_cn(expected_code: int, api_response: Dict[str, Any]):
    """验证响应状态码"""
    actual_code = api_response.get("code", 0)
    assert actual_code == expected_code
```

### 3. Specs（数据工厂层 - factory_boy）

**职责**：使用 factory_boy 自动创建实体，处理关联关系。

**核心特性**：
- `SubFactory` 自动创建关联实体
- `LazyAttribute` 计算派生字段
- `Trait` 定义特定状态

**示例**：

```python
class OrderSpec(BaseFactory):
    """订单 Spec"""
    class Meta:
        model = OrderEntity
        exclude = ("_user", "_product")

    # 关联实体 - 自动创建
    _user = factory.SubFactory(UserSpec)
    _product = factory.SubFactory(ProductSpec)

    # 外键字段
    user_id = factory.SelfAttribute("_user.id")
    product_id = factory.SelfAttribute("_product.id")

    # Trait: 已支付
    class Params:
        paid = factory.Trait(status="paid")
```

### 4. Entities（实体层 - SQLAlchemy）

**职责**：ORM 映射数据库表，定义关联关系。

**示例**：

```python
class UserEntity(Base):
    """用户实体"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    # ...

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "username": self.username,
            "email": self.email,
            # ...
        }
```

### 5. Repository（数据访问层）

**职责**：封装数据访问，支持自动清理。

**示例**：

```python
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
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session: Session):
    """自动清理测试数据"""
    yield
    # 测试结束后清理所有以 AUTO- 开头的数据
    repos = [UserRepo(db_session), ProductRepo(db_session), ...]
    for repo in repos:
        repo.delete_by_pattern("AUTO-%")
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
pip install pytest pytest-bdd factory_boy sqlalchemy pymysql requests
```

### 2. 配置环境

编辑 `config/settings.py`：

```python
BASE_URL = "http://localhost:8000"
DB_URL = "mysql+pymysql://root:mP123456&@mangotestingplatform-db-1:3306/mango_mock?charset=utf8mb4"
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
假如存在"用户"
当 使用用户ID GET "/users?id=${user.id}"

# ❌ 错误：硬编码 ID
当 GET "/users?id=123"
```

### 2. 使用 Spec 创建数据

```python
# ✅ 正确：使用 Spec 自动创建关联实体
order = OrderSpec()  # 自动创建用户和产品

# ❌ 错误：手动创建所有关联实体
user = UserSpec()
product = ProductSpec()
order = OrderSpec(user_id=user.id, product_id=product.id)
```

### 3. 使用 Trait 定义特定状态

```python
# 创建已支付的订单
order = OrderSpec(paid=True)

# 创建部门经理审批通过的报销
reimbursement = ReimbursementSpec(dept_approved=True)
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
| **data** | GET/POST /data | 数据提交 |
| **file** | GET/POST /files | 文件管理 |
| **reimbursement** | GET/POST/PUT/DELETE /reimbursements | 报销申请 |
| **approval** | POST /approvals/dept/finance/ceo | 三级审批 |
| **system** | GET /system/health/logs | 系统状态 |

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
- [factory_boy 文档](https://factoryboy.readthedocs.io/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
