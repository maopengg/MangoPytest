# MangoPytest pytest_api_mock - 数据工厂与自动化测试框架演示

## 项目概述

本项目是一个基于 pytest 的自动化测试框架演示项目，展示了如何使用数据工厂（Data Factory）模式来构建可维护、可扩展的 API 自动化测试。项目采用**五层架构设计**，实现了测试数据与测试逻辑的分离。

**核心特性**：

- **五层架构**：L5→L4→L3→L2→L1 分层设计，职责清晰
- **Pydantic 实体**：L3 使用 Pydantic 定义数据模型，提供 `to_api_payload()` 方法
- **数据流向**：L3 Entity 是唯一数据定义源头，贯穿各层
- **依赖自动解决**：A→B→C→D 链式依赖自动构造，无需手动准备
- **环境自适应**：同一套代码，自动适配 dev/test/prod/ci 环境
- **参数化场景**：业务变体自动生成，笛卡尔积覆盖组合场景
- **自动清理**：Fixture 自动清理测试数据

---

## 五层架构

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│  L5: 用例层 (Test Case)                                  │
│  ├── 单接口测试（60%）- 本模块逻辑、边界、异常            │
│  ├── 模块集成测试（30%）- 真实依赖验证                    │
│  └── 端到端测试（10%）- 完整业务闭环                      │
│  职责：测试执行与断言，调用 L4 Scenario                   │
├─────────────────────────────────────────────────────────┤
│  L4: 场景层 (Scenario) - 业务语义封装                    │
│  ├── 变体矩阵（VariantMatrix）- 参数化组合生成用例         │
│  ├── 依赖声明（Dependencies）- 自动解决前置数据           │
│  ├── 创建声明（Creates）- 声明场景创建的实体              │
│  └── 业务编排（Orchestrate）- 状态机驱动流程               │
│  职责：业务编排，使用 L3 Entity 生成/操作数据              │
├─────────────────────────────────────────────────────────┤
│  L3: 实体层 (Entity) - Pydantic 数据模型                  │
│  ├── 领域属性 - 业务字段强类型定义（Pydantic Field）       │
│  ├── 业务行为 - login()/approve()/submit() 等方法         │
│  ├── 工厂方法 - admin()/locked()/with_budget() 智能构造   │
│  └── to_api_payload() - 唯一数据序列化方法                │
│  职责：数据模型 + 业务逻辑，提供 to_api_payload()          │
├─────────────────────────────────────────────────────────┤
│  L2: 构造器层 (Builder) - 接收 Entity，调用 L1            │
│  ├── 接收 L3 Entity                                       │
│  ├── 调用 entity.to_api_payload() 获取 Dict               │
│  ├── 调用 L1 API 创建/更新/删除数据                       │
│  ├── 更新 Entity 状态（order_id 等响应字段）               │
│  └── 记录创建的数据 ID，支持 cleanup() 清理               │
│  职责：接收 Entity，调用 to_api_payload() 后传给 L1        │
├─────────────────────────────────────────────────────────┤
│  L1: 接口层 (API Manager) - HTTP 通信                     │
│  ├── 请求封装 - HTTP/HTTPS 请求统一封装                   │
│  ├── 加密解密 - 请求/响应数据的加解密处理                   │
│  ├── 认证管理 - Token、签名等认证机制                     │
│  ├── 协议适配 - REST/GraphQL/WebSocket 协议适配          │
│  └── 异常处理 - 接口级异常分类与处理                      │
│  职责：只接收 Dict，返回 Dict，不关心 Entity               │
└─────────────────────────────────────────────────────────┘
```

### 数据流向

```
L5 (Test Case) 
    ↓ 调用
L4 (Scenario) - 业务编排
    ↓ 使用 L3 生成/操作数据
L3 (Entity) - Pydantic 数据模型 + 业务逻辑
    ↓ to_api_payload()
L2 (Builder) - 接收 Entity，调用 to_api_payload() 后传给 L1
    ↓ 传递 Dict
L1 (API) - HTTP 通信，只接收 Dict，返回 Dict
    ↓ HTTP
   后端服务
```

### 核心设计原则

**1. L3 Entity 是唯一数据定义源头**

- 字段只在 L3 Entity 中定义一次（包含请求字段和响应字段）
- 通过 `to_api_payload()` 方法提供给 L1/L2
- L2 Builder 接收 L3 Entity，调用 `to_api_payload()` 获取数据

**2. L3 Entity 使用 Pydantic，提供 `to_api_payload()` 方法**

```python
from pydantic import BaseModel, Field

class OrderEntity(BaseModel):
    order_id: str = ""              # 响应字段，创建后填充
    product_id: int = Field(default=1001, gt=0)  # 请求字段
    
    def to_api_payload(self) -> Dict[str, Any]:
        """请求参数序列化"""
        return {"product_id": self.product_id}
```

> **说明**：order_id 等响应字段在创建时为空，由 L2 Builder 调用 API 后更新到 Entity

**3. L2 Builder 接收 Entity，L1 API 只接收 Dict**

```python
# L2: 接收 Entity，调用 to_api_payload()
class OrderBuilder:
    def create_order(self, entity: OrderEntity) -> OrderEntity:
        payload = entity.to_api_payload()
        result = pytest_api_mock.order.create_order(payload)
        # 更新 entity 的响应字段（order_id, status 等）
        entity.order_id = result["data"]["order_id"]
        entity.status = result["data"]["status"]
        return entity

# L1: 只接收 Dict，不关心 Entity
class OrderAPI:
    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.post("/api/v1/orders", json=payload)
        return response.json()
```

---

## 功能完成度分析

| 功能模块                      | 层级     | 代码实现 | 测试用例覆盖 | 说明                                                                              |
|---------------------------|--------|---------|------------|---------------------------------------------------------------------------------|
| **API Manager（接口层）**      | **L1** | 100% | 100% | 请求封装、认证管理、异常处理全部实现，所有测试用例都在使用                              |
| **构造器层 (Builder)**        | **L2** | 100% | 100% | 接收 Entity，调用 to_api_payload()，级联清理支持，所有测试用例都在使用                   |
| **实体层 (Entity)**          | **L3** | 100% | 100% | Pydantic 模型，to_api_payload()，业务逻辑方法已实现，所有测试用例都在使用                 |
| **场景层 (Scenario)**        | **L4** | 100% | 60% | 依赖声明、业务编排已实现，`test_approval_workflow.py` 中有使用示例                      |
| **Context 对象**            | -      | 100% | 80% | `ctx.create()`, `ctx.use()` 等已实现，`test_approval_workflow.py` 等中有使用示例        |
| **test_context Fixture**     | -      | 100% | 80% | pytest fixture 已实现，`test_user.py`, `test_order.py` 等中有使用示例                   |
| **变体矩阵 (Variant Matrix)** | -      | 100% | 20% | 笛卡尔积生成已实现，仅在 `test_approval_workflow.py` 中有使用示例                        |
| **状态机 (State Machine)**   | -      | 100% | 0% | 状态流转、历史记录已实现，但**测试用例中尚未使用**                                       |
| **血缘追踪 (Lineage)**        | -      | 100% | 5% | 节点、图、追踪器已实现，但**测试用例中很少使用**                                         |
| **配置管理 (Config)**         | -      | 100% | 100% | 环境自适应已实现，通过 `settings.py` 自动检测环境                                        |
| **Fixture 分层**            | -      | 100% | 100% | entities/, builders/, scenarios/ 分层结构已实现并广泛使用                                |
| **@case_data 装饰器**       | -      | 100% | 0% | 场景变体自动展开已实现，但**测试用例中尚未使用**                                         |

**总体完成度：约 85%**（代码实现 100%，测试用例覆盖 70%）

> **说明**：所有核心功能代码已实现，但部分高级功能（状态机、血缘追踪、@case_data 装饰器）在测试用例中的使用示例较少，需要补充更多实际使用案例。

### 待补充使用示例的功能

以下功能代码已实现，但在测试用例中**缺少实际使用示例**，需要补充：

| 功能 | 实现位置 | 缺少使用示例的测试文件 |
|-----|---------|---------------------|
| **血缘追踪 (Lineage)** | `data_factory/lineage/` | 除 `test_approval_workflow.py` 外 |
| **@case_data 装饰器** | `test_cases/decorators.py` | 所有测试文件 |

### 已充分使用的功能

以下功能已在测试用例中**充分使用**：

| 功能 | 使用示例位置 |
|-----|-------------|
| **五层架构 (L1-L5)** | 所有测试文件 |
| **Pydantic Entity** | `test_auth.py`, `test_user.py`, `test_product.py` 等 |
| **Builder 模式** | `test_user.py`, `test_reimbursement.py`, `test_order.py` 等 |
| **test_context Fixture** | `test_user.py`, `test_order.py`, `test_reimbursement.py`, `test_approval_workflow.py` |
| **Scenario 场景** | `test_approval_workflow.py` |

---

## 目录结构

```
auto_test/pytest_api_mock/
├── api_manager/          # 【L1: 接口层】API 管理层 - 统一接口封装与协议处理
│   ├── __init__.py       # 统一出口 pytest_api_mock
│   ├── auth.py           # 认证相关 API（Token管理、签名生成）
│   ├── user.py           # 用户管理 API
│   ├── product.py        # 产品管理 API
│   ├── order.py          # 订单管理 API
│   ├── reimbursement.py  # 报销申请 API
│   ├── dept_approval.py  # 部门审批 API
│   ├── finance_approval.py # 财务审批 API
│   ├── ceo_approval.py   # CEO审批 API
│   ├── file.py           # 文件上传 API
│   ├── data.py           # 数据提交 API
│   └── system.py         # 系统信息 API
│
├── data_factory/         # 数据工厂层 - 测试数据构建
│   ├── entities/         # 【L3: 实体层】Pydantic 数据模型 + 业务逻辑
│   │   ├── base_entity.py    # BaseEntity - Pydantic 基类
│   │   ├── user.py           # UserEntity
│   │   ├── reimbursement.py  # ReimbursementEntity
│   │   ├── dept_approval.py  # DeptApprovalEntity
│   │   ├── finance_approval.py # FinanceApprovalEntity
│   │   ├── ceo_approval.py   # CEOApprovalEntity
│   │   ├── org_entity.py     # OrgEntity
│   │   ├── budget_entity.py  # BudgetEntity
│   │   └── payment_entity.py # PaymentEntity
│   │
│   ├── builders/         # 【L2: 构造器层】接收 Entity，调用 L1
│   │   ├── base_builder.py   # BaseBuilder - 接收 Entity，级联清理
│   │   ├── user/
│   │   ├── reimbursement/
│   │   ├── payment/
│   │   ├── dept_approval/
│   │   ├── finance_approval/
│   │   ├── ceo_approval/
│   │   ├── product/
│   │   ├── order/
│   │   ├── file/
│   │   ├── data/
│   │   └── system/
│   │
│   ├── scenarios/        # 【L4: 场景层】业务编排
│   │   ├── base_scenario.py    # BaseScenario - 依赖声明、业务编排
│   │   ├── full_approval_scenario.py # 完整审批流场景
│   │   ├── login.py
│   │   ├── reimbursement.py
│   │   └── variant_matrix.py
│   │
│   ├── state_machine/    # 状态机层 - 实体状态管理
│   │   ├── state_machine.py
│   │   └── user_state_machine.py
│   │
│   ├── lineage/          # 血缘追踪层 - 数据血缘管理
│   │   ├── node.py
│   │   ├── graph.py
│   │   ├── tracker.py
│   │   └── analyzer.py
│   │
│   └── context.py        # Context 对象 - 统一管理实体创建和复用
│
├── fixtures/             # pytest Fixtures【分层结构】
│   ├── conftest.py       # 全局 Fixture 配置
│   ├── infra/            # 基础设施 Fixtures
│   │   ├── client.py     # api_client, test_token
│   │   ├── context.py    # test_context
│   │   └── db.py         # db_session
│   ├── entities/         # 【L3】实体 Fixtures
│   │   ├── __init__.py
│   │   ├── user_fixtures.py    # admin_user, locked_user, employee_user
│   │   └── org_fixtures.py     # default_org, large_org, small_org
│   ├── builders/         # 【L2】构造器 Fixtures（分层）
│   │   ├── __init__.py
│   │   ├── d_fixtures.py       # D模块: org_builder, user_builder
│   │   ├── c_fixtures.py       # C模块: budget_builder
│   │   ├── b_fixtures.py       # B模块: reimb_builder
│   │   └── a_fixtures.py       # A模块: payment_builder
│   └── scenarios/        # 【L4】场景 Fixtures
│       ├── __init__.py
│       └── approval_fixtures.py # full_approval_scenario
│
├── test_cases/           # 【L5: 用例层】测试执行与断言
│   ├── base.py           # 测试分层基类
│   ├── decorators.py     # @case_data 装饰器
│   ├── test_auth.py
│   ├── test_user.py
│   ├── test_product.py
│   ├── test_order.py
│   ├── test_reimbursement.py
│   ├── test_dept_approval.py
│   ├── test_finance_approval.py
│   ├── test_ceo_approval.py
│   ├── test_approval_workflow.py
│   ├── test_file.py
│   ├── test_data.py
│   ├── test_system.py
│   └── test_new_architecture.py
│
├── examples/             # 示例代码
│   ├── strategy_demo.py
│   ├── state_machine_demo.py
│   ├── variant_matrix_demo.py
│   ├── test_layer_demo.py
│   ├── lineage_demo.py
│   └── complete_demo.py  # 完整功能演示
│
└── config/               # 配置管理
    ├── settings.py       # 策略配置和环境检测
    ├── dev.py
    ├── test.py
    ├── pre.py
    └── prod.py
```

---

## 核心模块功能说明

### 1. API Manager（接口管理层 - L1）

**职责**：作为五层架构的最底层（L1），负责与外部系统的接口通信，封装所有与接口相关的技术细节。只接收 Dict，返回 Dict。

**核心功能**：

- **请求封装**：统一封装 HTTP/HTTPS 请求，处理超时、重试、连接池等
- **加密解密**：请求数据的加密（如 AES、RSA）和响应数据的解密
- **认证管理**：Token 管理、签名生成、鉴权信息维护
- **协议适配**：支持 REST、GraphQL、WebSocket 等多种协议
- **异常处理**：接口级异常分类、错误码映射、异常转换

**使用示例**：

```python
from auto_tests.pytest_api_mock.api_manager import pytest_api_mock

# 设置认证 token
pytest_api_mock.auth.set_token("your_token")

# 调用用户 API - L1 只接收 Dict
result = pytest_api_mock.user.get_all_users()

# 调用订单 API - L1 只接收 Dict
result = pytest_api_mock.order.create_order({
    "product_id": 1,
    "quantity": 2,
    "user_id": 1
})
```

### 2. Data Factory（数据工厂 - L2/L3/L4）

#### 2.1 Entity（实体层 - L3）

**职责**：使用 Pydantic 定义数据模型，包含数据验证、业务逻辑和 `to_api_payload()` 方法。

**核心特性**：
- Pydantic BaseModel 强类型定义
- `to_api_payload()` 唯一数据序列化方法
- 业务逻辑方法（`can_pay()`, `is_expired()` 等）
- 工厂方法（`with_product()`, `default()` 等）

```python
from auto_tests.pytest_api_mock.data_factory.entities import OrderEntity

# 创建 L3 Entity
order = OrderEntity.with_product(product_id=1001, quantity=2)

# 使用业务逻辑方法
assert order.can_pay()
assert not order.is_expired()

# 获取 API 请求参数（传给 L2 → L1）
payload = order.to_api_payload()
```

#### 2.2 Builder（构造器层 - L2）

**职责**：接收 L3 Entity，调用 `to_api_payload()` 获取 Dict，调用 L1 API，更新 Entity 状态。

**核心特性**：
- 接收 L3 Entity
- 调用 `entity.to_api_payload()` 获取请求参数
- 调用 L1 API 创建/更新/删除数据
- 更新 Entity 的响应字段（order_id, status 等）
- 记录创建的 ID，支持 `cleanup()` 自动清理

```python
from auto_tests.pytest_api_mock.data_factory.builders import OrderBuilder
from auto_tests.pytest_api_mock.data_factory.entities import OrderEntity

# 创建 L2 Builder
builder = OrderBuilder(token="your_token")

# 创建 L3 Entity
order = OrderEntity.with_product(product_id=1001, quantity=2)

# L2 接收 Entity，调用 to_api_payload()，调用 L1，更新 Entity
created_order = builder.create_order(order)

# 使用响应字段
print(created_order.order_id)   # 后端生成的 ID
print(created_order.status)     # pending_payment
```

#### 2.3 Scenario（场景层 - L4）

**职责**：业务编排，使用 L3 Entity 生成/操作数据，调用 L2 Builder。

**核心特性**：
- 依赖声明（Dependencies）- 自动解决前置数据
- 变体矩阵（VariantMatrix）- 参数化组合生成用例
- 业务编排 - 状态机驱动流程

```python
from auto_tests.pytest_api_mock.data_factory.scenarios import CreateOrderScenario

# 执行 L4 Scenario
scenario = CreateOrderScenario()
result = scenario.execute(product_id=1001, quantity=2)

if result.success:
    # 获取 L3 Entity
    order = result.get_entity("order")
    print(f"订单创建成功，ID: {order.order_id}")
```

### 3. Fixtures（测试夹具）【分层结构】

#### 3.1 基础设施 Fixtures

```python
from auto_tests.pytest_api_mock.fixtures.infra import (
    api_client,      # API 客户端
    test_token,      # 测试 token
    test_context,    # 测试上下文
)
```

#### 3.2 实体 Fixtures（L3）

```python
from auto_tests.pytest_api_mock.fixtures.entities import (
    admin_user,      # 管理员用户
    locked_user,     # 已锁定用户
    employee_user,   # 员工用户
    default_org,     # 默认组织
    large_org,       # 大型组织
)
```

#### 3.3 构造器 Fixtures（L2）

```python
from auto_tests.pytest_api_mock.fixtures.builders import (
    # D模块（基础层）
    org_builder,     # 组织构造器
    user_builder,    # 用户构造器
    # C模块（预算层）
    budget_builder,  # 预算构造器
    # B模块（报销层）
    reimb_builder,   # 报销单构造器
    approved_reimbursement,  # 已审批报销单
    # A模块（付款层）
    payment_builder, # 付款单构造器
    paid_payment,    # 已付款付款单
)
```

#### 3.4 场景 Fixtures（L4）

```python
from auto_tests.pytest_api_mock.fixtures.scenarios import (
    full_approval_scenario,   # 完整审批流场景
    full_approval_result,     # 完整审批流结果
)
```

### 4. @case_data 装饰器

场景变体自动展开为多个测试用例：

```python
from auto_tests.pytest_api_mock.test_cases.decorators import case_data
from auto_tests.pytest_api_mock.data_factory.scenarios import LoginScenario

# 单变体测试
@case_data(scenario=LoginScenario.variant(actor="admin", credential="correct"))
def test_login_success(self, test_context):
    result = test_context.get("result")
    assert result["success"] is True

# 多变体批量测试（自动生成12条用例）
@case_data(scenario=LoginScenario.all_variants())
def test_login_all_combinations(self, test_context):
    result = test_context.get("result")
    expected = result["expected"]
    assert result["success"] == expected["success"]
```

---

## 测试分层

| 层级 | 类型 | 占比 | 用途 |
|------|------|------|------|
| L5 | 单接口测试 | 60% | 验证本模块逻辑、边界、异常 |
| L5 | 模块集成测试 | 30% | 验证真实依赖（A→B→C→D） |
| L5 | 端到端测试 | 10% | 验证完整业务闭环 |

### 单接口测试示例（60%）

```python
@allure.feature("订单管理")
@allure.story("创建订单")
class TestCreateOrder(UnitTest):
    """创建订单接口测试 - 单接口测试（60%）"""
    
    @allure.title("正常创建订单 - 使用 L3 Entity")
    def test_create_order_success(self, api_client, order_builder):
        """测试正常创建订单"""
        # 1. 使用 L3 创建 Entity
        order = OrderEntity.with_product(product_id=1001, quantity=2)
        
        # 2. 传给 L2 创建订单
        result = order_builder.create_order(order)
        
        # 3. 断言
        assert result is not None
        assert result.order_id
        assert result.status == "pending_payment"
```

### 模块集成测试示例（30%）

```python
@allure.feature("订单管理")
@allure.story("订单全流程")
class TestOrderIntegration(UnitTest):
    """订单集成测试 - 模块集成测试（30%）"""
    
    @allure.title("创建-查询-取消订单流程")
    def test_create_query_cancel_flow(self, api_client):
        """测试订单创建、查询、取消流程"""
        # 1. 创建订单（L3 → L2 → L1）
        order = OrderEntity.with_product(product_id=1001, quantity=2)
        builder = OrderBuilder()
        created = builder.create_order(order)
        
        # 2. 查询订单（直接调用 L1）
        queried = pytest_api_mock.order.get_order(created.order_id)
        
        # 3. 取消订单
        cancelled = pytest_api_mock.order.cancel_order(created.order_id)
        
        assert cancelled["code"] == 200
```

### 端到端测试示例（10%）

```python
@allure.feature("订单管理")
@allure.story("订单完整生命周期")
class TestOrderE2E(UnitTest):
    """订单端到端测试 - 完整业务闭环（10%）"""
    
    @allure.title("完整订单生命周期：创建-支付-发货-完成")
    def test_order_full_lifecycle(self, api_client):
        """测试订单完整生命周期"""
        # 1. 创建订单
        order = OrderEntity.with_product(product_id=1001, quantity=2)
        builder = OrderBuilder()
        created = builder.create_order(order)
        
        # 2. 支付订单
        api_client.order.pay_order(created.order_id, "alipay")
        
        # 3. 发货
        api_client.order.ship_order(created.order_id)
        
        # 4. 完成
        api_client.order.complete_order(created.order_id)
        
        # 5. 验证最终状态
        final = api_client.order.get_order(created.order_id)
        assert final["data"]["status"] == "completed"
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制配置文件
cp config/dev.py.example config/dev.py

# 编辑配置文件，设置 API 地址和认证信息
vim config/dev.py
```

### 3. 运行测试

```bash
# 运行所有测试
pytest auto_tests/pytest_api_mock/test_cases/

# 运行特定模块
pytest auto_tests/pytest_api_mock/test_cases/test_order.py

# 运行特定测试
pytest auto_tests/pytest_api_mock/test_cases/test_order.py::TestCreateOrder::test_create_order_success

# 生成 Allure 报告
pytest auto_tests/pytest_api_mock/test_cases/ --alluredir=./allure-results
allure serve ./allure-results
```

---

## 最佳实践

### 1. 遵循五层架构

```python
# ✅ 正确：L5 调用 L4，L4 使用 L3，L3 传给 L2，L2 调用 L1
def test_with_scenario(self, test_context):
    result = test_context.scenario(CreateOrderScenario, product_id=1001)
    assert result.success

# ❌ 错误：在测试用例中直接调用 API
def test_wrong(self, api_client):
    result = api_client.post("/api/orders", json={"product_id": 1001})
    assert result.status_code == 200
```

### 2. 使用 L3 Entity 的 to_api_payload()

```python
# ✅ 正确：L3 提供 to_api_payload()，L2 调用，L1 只接收 Dict
class OrderBuilder:
    def create_order(self, entity: OrderEntity):
        payload = entity.to_api_payload()  # L3 提供
        return pytest_api_mock.order.create_order(payload)

# ❌ 错误：在 L2 中重复定义字段
class OrderBuilder:
    def create_order(self, product_id, quantity):
        payload = {  # 重复定义
            "product_id": product_id,
            "quantity": quantity,
        }
        return pytest_api_mock.order.create_order(payload)
```

### 3. 使用 Fixture 自动清理

```python
# ✅ 正确：使用 yield fixture 自动清理
@pytest.fixture
def order_builder():
    builder = OrderBuilder()
    yield builder
    builder.cleanup()  # 自动清理

# ❌ 错误：在测试用例中写清理逻辑
def test_wrong(self):
    builder = OrderBuilder()
    try:
        # 测试代码
    finally:
        builder.cleanup()  # 不应该在测试用例中写
```

### 4. 遵循测试分层比例

```python
# ✅ 正确：60% 单接口测试
class TestCreateOrder(UnitTest):
    def test_create_order_success(self): ...
    def test_create_order_validation_error(self): ...
    def test_create_order_out_of_stock(self): ...

# ✅ 正确：30% 集成测试
class TestOrderIntegration(UnitTest):
    def test_create_query_cancel_flow(self): ...

# ✅ 正确：10% 端到端测试
class TestOrderE2E(UnitTest):
    def test_order_full_lifecycle(self): ...
```

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

MIT License

---

## 联系方式

- 项目地址：https://github.com/your-org/mangopytest
- 问题反馈：https://github.com/your-org/mangopytest/issues
- 文档地址：https://mangopytest.readthedocs.io
