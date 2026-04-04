# MangoPytest Demo Project - 数据工厂与自动化测试框架演示

## 项目概述

本项目是一个基于 pytest 的自动化测试框架演示项目，展示了如何使用数据工厂（Data Factory）模式来构建可维护、可扩展的 API
自动化测试。项目采用分层架构设计，包含 Entity、Builder、Scenario、Strategy 等多个层次，实现了测试数据与测试逻辑的分离。

**核心特性**：

- **领域驱动设计**：业务实体封装数据与行为，非静态配置
- **依赖自动解决**：A→B→C→D 链式依赖自动构造，无需手动准备
- **环境自适应**：同一套代码，自动适配 dev/test/prod/ci 环境
- **参数化场景**：业务变体自动生成，笛卡尔积覆盖组合场景
- **全链路追踪**：数据血缘自动记录，故障一键定位
- **状态机驱动**：实体状态流转自动化，支持复杂业务场景

## 功能完成度分析

| 功能模块                      | 层级   | 完成度  | 说明                                                                              |
| ------------------------- | ------ | ---- | ------------------------------------------------------------------------------- |
| **API Manager（接口层）**     | **L1** | 100% | 请求封装、加密解密、认证管理、协议适配、异常处理全部实现                                    |
| **策略层 (Strategy)**        | **L2** | 100% | API/Mock/DB/Hybrid 策略已实现                                                        |
| **构造器层 (Builder)**        | **L2** | 95%  | 基础 Builder 实现，智能依赖解决，级联清理支持                                                     |
| **实体层 (Entity)**          | **L3** | 100% | UserEntity, ReimbursementEntity, OrgEntity, BudgetEntity, PaymentEntity 已实现     |
| **场景层 (Scenario)**        | **L4** | 100% | 依赖声明、变体矩阵、业务编排、预期结果验证全部实现                                                       |
| **Context 对象**            | -      | 100% | `ctx.create()`, `ctx.use()`, `ctx.action()`, `ctx.expect()`, `ctx.event()` 全部实现 |
| **状态机 (State Machine)**   | -      | 100% | 状态流转、历史记录已实现                                                                    |
| **变体矩阵 (Variant Matrix)** | -      | 100% | 笛卡尔积生成、约束过滤已实现                                                                  |
| **血缘追踪 (Lineage)**        | -      | 100% | 节点、图、追踪器、分析器已实现                                                                 |
| **配置管理 (Config)**         | -      | 100% | 环境自适应、策略配置化已实现                                                                  |
| **Fixture 分层**            | -      | 100% | entities/, builders/, scenarios/ 分层结构已实现                                        |
| **test\_context Fixture** | -      | 100% | pytest fixture 已实现                                                              |
| **@case\_data 装饰器**       | -      | 100% | 场景变体自动展开已实现                                                                     |
| **core/ 框架层**             | -      | 100% | API、Models、Utils 跨项目复用组件已实现                                                     |

**总体完成度：约 98%**

## 项目架构

### 五层架构

```
┌─────────────────────────────────────────────────────────┐
│  L5: 用例层 (Test Case)                                  │
│  ├── 单接口测试（60%）- 本模块逻辑、边界、异常            │
│  ├── 模块集成测试（30%）- 真实依赖验证                    │
│  └── 端到端测试（10%）- 完整业务闭环                      │
├─────────────────────────────────────────────────────────┤
│  L4: 场景层 (Scenario) - 业务语义封装                    │
│  ├── 变体矩阵（VariantMatrix）- 参数化组合生成用例         │
│  ├── 依赖声明（Dependencies）- 自动解决前置数据           │
│  ├── 创建声明（Creates）- 声明场景创建的实体              │
│  └── 业务编排（Orchestrate）- 状态机驱动流程               │
├─────────────────────────────────────────────────────────┤
│  L3: 实体层 (Entity) - 领域对象定义                       │
│  ├── 领域属性 - 业务字段强类型定义                         │
│  ├── 业务行为 - login()/approve()/submit() 等方法         │
│  └── 工厂方法 - admin()/locked()/with_budget() 智能构造   │
├─────────────────────────────────────────────────────────┤
│  L2: 策略层 (Strategy) - 构造与持久化                    │
│  ├── APIStrategy - 调用REST/GraphQL接口（默认）           │
│  ├── DBStrategy - 直接SQL插入（批量/性能）                │
│  ├── HybridStrategy - API头+DB明细（复杂对象）            │
│  └── MockStrategy - 本地内存对象（单元测试）              │
├─────────────────────────────────────────────────────────┤
│  L1: 接口层 (API Manager) - 接口通信与协议处理            │
│  ├── 请求封装 - HTTP/HTTPS 请求统一封装                   │
│  ├── 加密解密 - 请求/响应数据的加解密处理                   │
│  ├── 认证管理 - Token、签名等认证机制                     │
│  ├── 协议适配 - REST/GraphQL/WebSocket 协议适配          │
│  └── 异常处理 - 接口级异常分类与处理                      │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
auto_test/demo_project/
├── api_manager/          # 【L1: 接口层】API 管理层 - 统一接口封装与协议处理
│   ├── __init__.py       # 统一出口 demo_project
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
├── core/                 # 【框架层】跨项目复用
│   ├── __init__.py
│   ├── api/              # 统一 API 客户端
│   │   ├── __init__.py
│   │   ├── client.py     # APIClient - HTTP 请求封装
│   │   ├── auth.py       # AuthManager - 认证管理
│   │   └── exceptions.py # API 异常类
│   ├── models/           # 共享数据模型
│   │   ├── __init__.py
│   │   ├── base.py       # BaseModel - 基础模型
│   │   ├── entity.py     # BaseEntity - 实体基类
│   │   └── result.py     # Result - 结果模型
│   └── utils/            # 通用工具
│       ├── __init__.py
│       ├── decorators.py # retry, timer, validate 装饰器
│       └── helpers.py    # generate_id, merge_dicts 等辅助函数
│
├── data_factory/         # 数据工厂层 - 测试数据构建
│   ├── entities/         # 实体层 - 数据模型定义
│   │   ├── base_entity.py
│   │   ├── user.py
│   │   ├── reimbursement.py
│   │   ├── dept_approval.py
│   │   ├── finance_approval.py
│   │   ├── ceo_approval.py
│   │   ├── org_entity.py       # 组织实体
│   │   ├── budget_entity.py    # 预算实体
│   │   └── payment_entity.py   # 付款单实体
│   │
│   ├── builders/         # 构造器层 - 数据构建与 API 调用
│   │   ├── base_builder.py     # 增强版 - 智能依赖解决
│   │   ├── user/
│   │   ├── reimbursement/
│   │   ├── payment/            # 【新增】PaymentBuilder
│   │   ├── dept_approval/
│   │   ├── finance_approval/
│   │   ├── ceo_approval/
│   │   ├── product/
│   │   ├── order/
│   │   ├── file/
│   │   ├── data/
│   │   └── system/
│   │
│   ├── scenarios/        # 场景层 - 业务流程封装
│   │   ├── base_scenario.py    # 增强版 - 依赖声明、业务编排
│   │   ├── full_approval_scenario.py # 【新增】完整审批流场景
│   │   ├── login.py
│   │   ├── reimbursement.py
│   │   └── variant_matrix.py
│   │
│   ├── strategies/       # 策略层 - 数据构造策略
│   │   ├── base_strategy.py
│   │   ├── api_strategy.py
│   │   ├── mock_strategy.py
│   │   ├── db_strategy.py
│   │   └── hybrid_strategy.py
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
│   │   ├── context.py    # test_context【新增】
│   │   └── db.py         # db_session
│   ├── entities/         # 【新增】实体 Fixtures
│   │   ├── __init__.py
│   │   ├── user_fixtures.py    # admin_user, locked_user, employee_user
│   │   └── org_fixtures.py     # default_org, large_org, small_org
│   ├── builders/         # 【新增】构造器 Fixtures（分层）
│   │   ├── __init__.py
│   │   ├── d_fixtures.py       # D模块: org_builder, user_builder
│   │   ├── c_fixtures.py       # C模块: budget_builder
│   │   ├── b_fixtures.py       # B模块: reimb_builder
│   │   └── a_fixtures.py       # A模块: payment_builder
│   └── scenarios/        # 【新增】场景 Fixtures
│       ├── __init__.py
│       └── approval_fixtures.py # full_approval_scenario
│
├── test_cases/           # 测试用例层
│   ├── base.py           # 测试分层基类
│   ├── decorators.py     # 【新增】@case_data 装饰器
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

## 核心模块功能说明

### 0. Context 对象

统一管理实体创建、复用、业务动作执行：

```python
from auto_test.demo_project.data_factory.context import Context
from auto_test.demo_project.data_factory.entities import UserEntity, OrgEntity

with Context(auto_cleanup=True) as ctx:
    # 1. 创建实体
    user = ctx.create(UserEntity, username="test_user", role="admin")
    org = ctx.create(OrgEntity, name="测试组织", budget_total=100000)

    # 2. 复用实体
    existing_user = ctx.use(UserEntity, role="admin")

    # 3. 执行业务动作
    result = ctx.action(user.validate)

    # 4. 验证预期
    is_valid = ctx.expect(user.username).equals("test_user")

    # 5. 事件追踪
    ctx.fire_event("user_created", priority="normal")
    fired = ctx.event("user_created").was_fired()
```

### 1. API Manager（接口管理层 - L1）

**职责**：作为五层架构的最底层（L1），负责与外部系统的接口通信，封装所有与接口相关的技术细节。

**核心功能**：
- **请求封装**：统一封装 HTTP/HTTPS 请求，处理超时、重试、连接池等
- **加密解密**：请求数据的加密（如 AES、RSA）和响应数据的解密
- **认证管理**：Token 管理、签名生成、鉴权信息维护
- **协议适配**：支持 REST、GraphQL、WebSocket 等多种协议
- **异常处理**：接口级异常分类、错误码映射、异常转换

**使用示例**：

```python
from auto_test.demo_project.api_manager import demo_project

# 设置认证 token
demo_project.auth.set_token("your_token")

# 调用用户 API
result = demo_project.user.get_all_users()

# 调用订单 API
result = demo_project.order.create_order(
    product_id=1,
    quantity=2,
    user_id=1
)
```

**模块组成**：

| 模块 | 功能说明 |
|------|----------|
| `auth.py` | 认证管理：Token 获取、刷新、签名生成 |
| `user.py` | 用户管理 API：用户 CRUD、权限查询 |
| `product.py` | 产品管理 API：产品信息、库存查询 |
| `order.py` | 订单管理 API：订单创建、查询、取消 |
| `reimbursement.py` | 报销申请 API：报销单提交、查询 |
| `dept_approval.py` | 部门审批 API：审批操作、状态查询 |
| `finance_approval.py` | 财务审批 API：财务审核、打款 |
| `ceo_approval.py` | CEO 审批 API：最终审批 |
| `file.py` | 文件上传 API：文件上传、下载 |
| `data.py` | 数据提交 API：数据上报 |
| `system.py` | 系统信息 API：健康检查、配置查询 |

### 2. Data Factory（数据工厂 - L2/L3/L4）

#### 2.1 Entity（实体层 - L3）

定义数据模型，包含数据验证和生命周期管理：

```python
from auto_test.demo_project.data_factory.entities import ReimbursementEntity

# 创建实体
reimbursement = ReimbursementEntity(
    user_id=1,
    amount=1000.00,
    reason="差旅报销"
)

# 数据验证
assert reimbursement.validate() is True
```

#### 2.2 Builder（构造器层 - L2）

负责构造实体数据并调用 API 创建/更新/删除数据：

```python
from auto_test.demo_project.data_factory.builders import ReimbursementBuilder

# 创建 Builder
builder = ReimbursementBuilder(token="your_token")

# 快捷方法 - 创建并审批通过
reimbursement = builder.create_approved(
    user_id=1,
    amount=1000.00,
    reason="测试报销"
)
```

#### 2.3 Scenario（场景层 - L4）

封装完整的业务流程，支持依赖声明和业务编排：

```python
from auto_test.demo_project.data_factory.scenarios import FullApprovalScenario

# 执行完整审批流场景
scenario = FullApprovalScenario()
result = scenario.execute(amount=50000)

if result.success:
    reimbursement = result.get_entity("reimbursement")
    print(f"审批流程完成，报销ID: {reimbursement.id}")
```

#### 2.4 Strategy（策略层 - L2）

提供多种数据构造策略，支持不同测试场景：

```python
from auto_test.demo_project.data_factory.strategies import (
    APIContextStrategy,
    MockStrategy,
)

# API策略（默认）- 真实接口调用
api_strategy = APIContextStrategy(api_client)

# Mock策略 - 本地快速测试
mock_strategy = MockStrategy()
```

#### 2.5 State Machine（状态机层）

实体状态管理，支持状态流转和验证：

```python
from auto_test.demo_project.data_factory.state_machine import UserStateMachine

# 创建状态机
sm = UserStateMachine()

# 执行状态转换
sm.transition_to("locked")
```

#### 2.6 Lineage（血缘追踪层）

数据血缘自动记录和追踪：

```python
from auto_test.demo_project.data_factory.lineage import DataLineageTracker

# 创建追踪器
tracker = DataLineageTracker()

# 记录数据创建
tracker.record_creation("user", "user_001")
```

#### 2.7 Variant Matrix（变体矩阵层）

参数化测试，笛卡尔积自动生成用例：

```python
from auto_test.demo_project.data_factory.scenarios.variant_matrix import (
    VariantMatrix, Dimension, Variant
)

# 创建变体矩阵
matrix = VariantMatrix([
    Dimension("user_type", [
        Variant("admin", {"role": "admin"}, 0),
        Variant("normal", {"role": "user"}, 1),
    ]),
])

# 生成所有组合
variants = matrix.generate()
```

### 3. Fixtures（测试夹具）【分层结构】

#### 3.1 基础设施 Fixtures

```python
from auto_test.demo_project.fixtures.infra import (
    api_client,      # API 客户端
    test_token,      # 测试 token
    test_context,    # 测试上下文
)
```

#### 3.2 实体 Fixtures

```python
from auto_test.demo_project.fixtures.entities import (
    admin_user,      # 管理员用户
    locked_user,     # 已锁定用户
    employee_user,   # 员工用户
    default_org,     # 默认组织
    large_org,       # 大型组织
)
```

#### 3.3 构造器 Fixtures（分层）

```python
from auto_test.demo_project.fixtures.builders import (
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

#### 3.4 场景 Fixtures

```python
from auto_test.demo_project.fixtures.scenarios import (
    full_approval_scenario,   # 完整审批流场景
    full_approval_result,     # 完整审批流结果
)
```

### 4. @case\_data 装饰器

场景变体自动展开为多个测试用例：

```python
from auto_test.demo_project.test_cases.decorators import case_data
from auto_test.demo_project.data_factory.scenarios import LoginScenario

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

### 5. core/ 框架层

跨项目复用的核心组件：

```python
from auto_test.demo_project.core import APIClient, BaseEntity, Result
from auto_test.demo_project.core.api import AuthManager
from auto_test.demo_project.core.utils import retry, timer, generate_id

# API 客户端
client = APIClient(base_url="https://api.example.com")
response = client.get("/users")

# 结果模型
result = Result.success(data={"id": 1})

# 装饰器
@retry(max_attempts=3, delay=1.0)
def api_call():
    pass

# 辅助函数
id = generate_id("user")  # "user_a1b2c3d4"
```

### 6. 配置管理

```python
from auto_test.demo_project.config.settings import settings, CreateStrategy, Environment

print(f"当前环境: {settings.ENV.value}")
print(f"默认策略: {settings.DEFAULT_STRATEGY.value}")
```

## 执行用例全流程

### 1. 环境准备

```bash
# 进入项目目录
cd d:\code\MangoPytest

# 启动 FastAPI Mock 服务
python service/mock_api.py

# 服务将启动在 http://localhost:8003
```

### 2. 执行测试用例

```bash
# 执行所有测试用例
python -m pytest auto_test/demo_project/test_cases/ -v

# 执行并生成 Allure 报告
python -m pytest auto_test/demo_project/test_cases/ -v --alluredir=./allure-results
```

### 3. 运行示例演示

```bash
# 完整功能演示
python auto_test/demo_project/examples/complete_demo.py
```

## 快速开始示例

### 示例1：使用 Fixture 简化测试

```python
# 使用实体 fixtures
def test_with_admin(admin_user):
    assert admin_user.role == "admin"
    assert admin_user.is_active()

# 使用构造器 fixtures（分层）
def test_with_builder(user_builder):
    user = user_builder.create(username="test")
    assert user.id is not None

# 使用场景 fixtures
def test_with_scenario(full_approval_scenario):
    result = full_approval_scenario.execute(amount=50000)
    assert result.success
```

### 示例2：使用 @case\_data 装饰器

```python
from auto_test.demo_project.test_cases.decorators import case_data
from auto_test.demo_project.data_factory.scenarios import LoginScenario

class TestLogin:
    @case_data(scenario=LoginScenario.variant(actor="admin", credential="correct"))
    def test_login_success(self, test_context):
        result = test_context.get("result")
        assert result["success"] is True
    
    @case_data(scenario=LoginScenario.all_variants())
    def test_login_all(self, test_context):
        result = test_context.get("result")
        assert result["success"] == result["expected"]["success"]
```

### 示例3：使用 core/ 框架层

```python
from auto_test.demo_project.core import APIClient, Result
from auto_test.demo_project.core.utils import retry, generate_id

# API 客户端
client = APIClient(base_url="https://api.example.com")
response = client.get("/users", retry_count=3)

# 结果处理
result = Result.success(data={"id": 1})
if result.is_success:
    print(result.data)
```

## 最佳实践

1. **使用 Fixture 分层结构** - entities/ builders/ scenarios/
2. **使用 @case\_data 装饰器** - 自动展开场景变体
3. **使用 test\_context** - 统一追踪和清理测试数据
4. **使用 Builder 快捷方法** - create\_approved, create\_paid 等
5. **使用 core/ 框架层** - 跨项目复用核心组件
6. **分层测试** - 单元测试（快）→ 集成测试（真）→ 端到端测试（全）

## 技术栈

- **Python 3.10+**
- **pytest** - 测试框架
- **requests** - HTTP 客户端
- **pydantic** - 数据验证
- **FastAPI** - Mock API 服务
- **Allure** - 测试报告

## Allure 报告集成

本项目已集成 Allure 报告框架，将架构功能可视化到测试报告中。

### 快速开始

```bash
# 安装 allure-pytest
pip install allure-pytest

# 执行测试并生成 Allure 报告
python -m pytest auto_test/demo_project/test_cases/ -v --alluredir=./allure-results

# 查看 Allure 报告
allure serve ./allure-results
```

### 核心功能

1. **Context 操作自动记录** - create/use/action/expect/event 操作自动附加到报告
2. **数据血缘追踪** - 数据依赖关系图自动可视化
3. **场景变体信息** - 变体矩阵参数自动记录
4. **状态机流转** - 状态转换历史自动附加
5. **构造器依赖** - 依赖链自动记录

### 使用示例

```python
from auto_test.demo_project.fixtures.allure_conftest import allure_feature, allure_story

@allure_feature("用户管理")
@allure_story("用户创建")
def test_create_user(allure_context):
    """创建用户并验证"""
    # 创建用户（自动记录到 Allure）
    user = allure_context.create(UserEntity, username="test", role="admin")
    
    # 验证（自动记录到 Allure）
    assert user.role == "admin"
```

详见 [ALLURE\_GUIDE.md](ALLURE_GUIDE.md)

## 许可证

MIT License
