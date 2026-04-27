# API Mock - API 自动化测试框架

## 项目概述

本项目是一个基于 **pytest** 和 **抽象页面对象模式** 的 API 自动化测试框架，针对 Mango Mock API 服务进行测试。采用分层架构设计，将 API 调用、测试数据和测试用例分离，实现高可维护性和可扩展性。

**核心特性**：

- **抽象页面对象模式**：API 抽象层封装 HTTP 请求，业务层专注测试逻辑
- **多环境配置**：支持 dev/test/pre/prod 环境切换
- **数据驱动测试**：支持参数化测试用例
- **Allure 报告**：集成 Allure 生成美观的测试报告
- **自动重试机制**：失败请求自动重试
- **统一日志记录**：完整的请求/响应日志

---

## 架构设计

### 五层架构

```
L5: Test Cases 测试用例层
    ├── 测试执行与断言
    ├── 使用 fixtures 准备数据
    └── 调用 L4 抽象层方法
    ↓
L4: Abstract 抽象层
    ├── 按业务域分包（auth/user/product/order/...）
    ├── 封装业务操作（login/create_order/approve）
    └── 组合多个 L3 API 调用
    ↓
L3: API Manager 接口管理层
    ├── 封装原始 HTTP 请求（GET/POST/PUT/DELETE）
    ├── 处理请求头、认证信息
    └── 统一错误处理
    ↓
L2: HTTP Client 通信层
    ├── requests 库封装
    ├── 自动重试机制
    └── 日志记录
    ↓
L1: Mock API Service
    └── 后端服务（FastAPI）
```

### 数据流向

```
Test Case（测试用例）
    ↓ 调用
Abstract Layer（业务抽象）
    ↓ 组合调用
API Manager（接口管理）
    ↓ HTTP 请求
Mock API Service（后端服务）
    ↓ 响应
Test Case（断言验证）
```

---

## 目录结构

```
auto_tests/api_mock/
├── abstract/               # 抽象层（业务封装）
│   ├── auth/               # 认证模块
│   │   ├── __init__.py
│   │   └── auth.py         # 登录、注册等业务操作
│   ├── user/               # 用户模块
│   ├── product/            # 产品模块
│   ├── order/              # 订单模块
│   ├── data/               # 数据提交模块
│   ├── file/               # 文件模块
│   ├── reimbursement/      # 报销申请模块
│   ├── dept_approval/      # 部门审批模块（C级）
│   ├── finance_approval/   # 财务审批模块（B级）
│   ├── ceo_approval/       # 总经理审批模块（A级）
│   ├── workflow/           # 审批工作流模块
│   └── system/             # 系统管理模块
│
├── test_cases/             # 测试用例层
│   ├── test_auth/          # 认证测试
│   ├── test_user/          # 用户管理测试
│   ├── test_product/       # 产品管理测试
│   ├── test_order/         # 订单管理测试
│   ├── test_data/          # 数据提交测试
│   ├── test_file/          # 文件上传测试
│   ├── test_reimbursement/ # 报销申请测试
│   ├── test_dept_approval/ # 部门审批测试
│   ├── test_finance_approval/ # 财务审批测试
│   ├── test_ceo_approval/  # 总经理审批测试
│   ├── test_workflow/      # 审批流程测试
│   └── test_system/        # 系统测试
│
├── config/                 # 配置管理
│   ├── __init__.py         # 配置导出
│   ├── settings.py         # 多环境配置类
│   ├── .env.dev            # 开发环境变量
│   ├── .env.test           # 测试环境变量
│   ├── .env.pre            # 预发布环境变量
│   └── .env.prod           # 生产环境变量
│
└── README.md               # 本文档
```

---

## 核心模块功能说明

### 1. Abstract Layer（抽象层）

**职责**：封装业务操作，隐藏底层 API 调用细节。

**示例**：

```python
# abstract/auth/auth.py
class AuthAbstract:
    """认证抽象层"""
    
    def __init__(self):
        self.api = DemoProjectAPI()
    
    def login(self, username: str, password: str) -> dict:
        """用户登录，返回 token"""
        result = self.api.auth.api_login({
            "username": username,
            "password": password
        })
        return result["data"]
    
    def register_and_login(self, username: str, password: str) -> dict:
        """注册并登录"""
        self.api.auth.api_register({
            "username": username,
            "password": password
        })
        return self.login(username, password)
```

### 2. API Manager（接口管理层）

**职责**：封装原始 HTTP 请求，统一处理认证和错误。

**示例**：

```python
# api_manager/auth.py
class AuthAPI:
    """认证 API"""
    
    def __init__(self):
        self.client = DemoProjectBaseAPI()
    
    def api_login(self, data: dict) -> dict:
        """登录接口"""
        return self.client.post("/auth/login", json=data)
    
    def api_register(self, data: dict) -> dict:
        """注册接口"""
        return self.client.post("/auth/register", json=data)
```

### 3. Test Cases（测试用例层）

**职责**：编写测试用例，使用抽象层执行业务操作。

**示例**：

```python
# test_cases/test_auth/test_auth.py
class TestLogin:
    """登录测试"""
    
    def test_login_success(self):
        """测试正常登录"""
        auth = AuthAbstract()
        result = auth.login("testuser", "password123")
        assert result["token"] is not None
    
    def test_login_wrong_password(self):
        """测试密码错误"""
        auth = AuthAbstract()
        with pytest.raises(ApiError):
            auth.login("testuser", "wrong_password")
```

### 4. Config（配置管理）

**职责**：管理多环境配置，支持环境变量切换。

**示例**：

```python
# config/settings.py
class ApiMockConfig(BaseConfig):
    """基础配置"""
    PROJECT_NAME: str = "API Mock 自动化测试"
    MOCK_TIMEOUT: int = 30
    MOCK_RETRY_TIMES: int = 3

class DevConfig(ApiMockConfig):
    """开发环境"""
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8003"

class ProdConfig(ApiMockConfig):
    """生产环境"""
    ENV: str = "prod"
    BASE_URL: str = "http://43.142.161.61:8003"
```

---

## 测试分层

| 层级 | 类型 | 占比 | 用途 |
|------|------|------|------|
| Unit | 单接口测试 | 60% | 验证本模块逻辑、边界、异常 |
| Integration | 模块集成测试 | 30% | 验证真实依赖（A→B→C→D） |
| E2E | 端到端测试 | 10% | 验证完整业务闭环 |

---

## 快速开始

### 1. 安装依赖

```bash
pip install pytest allure-pytest requests pydantic
```

### 2. 配置环境

编辑 `config/settings.py` 或设置环境变量：

```bash
# Windows
set ENV=dev

# Linux/Mac
export ENV=dev
```

### 3. 运行测试

```bash
# 运行所有测试
pytest auto_tests/api_mock/

# 运行特定模块
pytest auto_tests/api_mock/test_cases/test_user/

# 运行特定测试类
pytest auto_tests/api_mock/test_cases/test_auth/test_auth.py::TestLogin

# 生成 Allure 报告
pytest auto_tests/api_mock/ --alluredir=reports/api_mock/allure
allure serve reports/api_mock/allure

# 按标签运行
pytest auto_tests/api_mock/ -m smoke
pytest auto_tests/api_mock/ -m integration
```

---

## 最佳实践

### 1. 抽象层设计原则

```python
# ✅ 正确：抽象层封装业务逻辑
class OrderAbstract:
    def create_order_with_product(self, user_id: int, product_id: int, quantity: int):
        """创建订单（自动计算总价）"""
        product = self.product_api.get(product_id)
        total = product["price"] * quantity
        return self.order_api.create({
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total": total
        })

# ❌ 错误：测试用例直接调用底层 API
def test_create_order():
    product = api.product.get(1)
    order = api.order.create({...})  # 测试用例太复杂
```

### 2. 测试用例编写规范

```python
# ✅ 正确：测试用例简洁明了
class TestUser:
    def test_create_user_success(self):
        """测试创建用户成功"""
        user = UserAbstract()
        result = user.create(username="test01")
        assert result["username"] == "test01"
    
    def test_create_user_duplicate(self):
        """测试重复用户名"""
        user = UserAbstract()
        with pytest.raises(ApiError) as e:
            user.create(username="testuser")  # 已存在
        assert e.value.code == 400

# ❌ 错误：测试用例包含太多细节
def test_user():
    # 直接操作 API，代码冗余
    response = requests.post(...)
    assert response.status_code == 200
    data = response.json()
    # ... 更多断言
```

### 3. 使用 Fixtures 准备数据

```python
# ✅ 正确：使用 fixtures 准备测试数据
@pytest.fixture
def new_user():
    """创建新用户 fixture"""
    user = UserAbstract()
    return user.create(username=f"test_{uuid.uuid4().hex[:6]}")

def test_update_user(new_user):
    """测试更新用户"""
    user = UserAbstract()
    result = user.update(new_user["id"], {"email": "new@test.com"})
    assert result["email"] == "new@test.com"
```

### 4. 多环境配置管理

```python
# 在测试用例中使用配置
from auto_tests.api_mock.config import get_config

config = get_config()
print(f"当前环境: {config.ENV}")
print(f"API地址: {config.BASE_URL}")
print(f"超时时间: {config.MOCK_TIMEOUT}")
```

---

## API 覆盖

### 已实现的 API 模块

| 模块 | API | 测试场景 |
|------|-----|----------|
| **auth** | POST /auth/login | 登录成功/失败 |
| **auth** | POST /auth/register | 用户注册 |
| **user** | GET /users | 获取用户列表 |
| **user** | POST /users | 创建用户 |
| **user** | PUT /users/{id} | 更新用户 |
| **user** | DELETE /users/{id} | 删除用户 |
| **product** | GET/POST/PUT/DELETE /products | 产品 CRUD |
| **order** | GET/POST/PUT/DELETE /orders | 订单 CRUD |
| **data** | POST /api/data | 数据提交 |
| **file** | POST /upload | 文件上传 |
| **reimbursement** | GET/POST/PUT/DELETE /reimbursements | 报销申请 |
| **dept_approval** | GET/POST /dept-approvals | 部门审批（C级） |
| **finance_approval** | GET/POST /finance-approvals | 财务审批（B级） |
| **ceo_approval** | GET/POST /ceo-approvals | 总经理审批（A级） |
| **workflow** | GET /workflow/{id} | 审批流程查询 |
| **system** | GET /health, /info | 系统状态 |

---

## 审批流程测试

### 四级审批工作流

```
D级（报销申请）→ C级（部门审批）→ B级（财务审批）→ A级（总经理审批）
     ↓                  ↓                  ↓                  ↓
   pending        dept_approved      finance_approved     ceo_approved
```

### 测试示例

```python
class TestApprovalWorkflow:
    """审批流程测试"""
    
    def test_full_approval_workflow(self):
        """测试完整四级审批流程"""
        # D级：创建报销申请
        reimb = ReimbursementAbstract().create(amount=1000)
        assert reimb["status"] == "pending"
        
        # C级：部门审批
        dept = DeptApprovalAbstract().approve(reimb["id"])
        assert dept["status"] == "approved"
        
        # B级：财务审批
        finance = FinanceApprovalAbstract().approve(reimb["id"], dept["id"])
        assert finance["status"] == "approved"
        
        # A级：总经理审批
        ceo = CEOApprovalAbstract().approve(reimb["id"], finance["id"])
        assert ceo["status"] == "approved"
```

---

## 参考

- [pytest 文档](https://docs.pytest.org/)
- [Allure 文档](https://docs.qameta.io/allure/)
- [requests 文档](https://requests.readthedocs.io/)
- [Pydantic 文档](https://docs.pydantic.dev/)

---

## 项目特点

1. **抽象页面对象模式**：业务逻辑与 HTTP 请求分离，易于维护
2. **多环境配置**：通过环境变量快速切换测试环境
3. **统一错误处理**：API 层统一处理异常，测试用例更简洁
4. **自动重试机制**：网络波动时自动重试请求
5. **完整日志记录**：请求/响应详细记录，便于问题排查
6. **Allure 报告**：美观的 HTML 测试报告，支持历史趋势
