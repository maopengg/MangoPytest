# MangoPytest Demo Project - 数据工厂与自动化测试框架演示

## 项目概述

本项目是一个基于 pytest 的自动化测试框架演示项目，展示了如何使用数据工厂（Data Factory）模式来构建可维护、可扩展的 API 自动化测试。项目采用分层架构设计，包含 Entity、Builder、Scenario、Strategy 等多个层次，实现了测试数据与测试逻辑的分离。

**核心特性**：

- **领域驱动设计**：业务实体封装数据与行为，非静态配置
- **依赖自动解决**：A→B→C→D 链式依赖自动构造，无需手动准备
- **环境自适应**：同一套代码，自动适配 dev/test/prod/ci 环境
- **参数化场景**：业务变体自动生成，笛卡尔积覆盖组合场景
- **全链路追踪**：数据血缘自动记录，故障一键定位
- **状态机驱动**：实体状态流转自动化，支持复杂业务场景

## 项目架构

### 四层架构

```
┌─────────────────────────────────────────────────────────┐
│  L4: 用例层 (Test Case)                                  │
│  ├── 单接口测试（60%）- 本模块逻辑、边界、异常            │
│  ├── 模块集成测试（30%）- 真实依赖验证                    │
│  └── 端到端测试（10%）- 完整业务闭环                      │
├─────────────────────────────────────────────────────────┤
│  L3: 场景层 (Scenario) - 业务语义封装                    │
│  ├── 变体矩阵（VariantMatrix）- 参数化组合生成用例         │
│  ├── 依赖声明（Dependencies）- 自动解决前置数据           │
│  └── 业务编排（Orchestrate）- 状态机驱动流程               │
├─────────────────────────────────────────────────────────┤
│  L2: 实体层 (Entity) - 领域对象定义                       │
│  ├── 领域属性 - 业务字段强类型定义                         │
│  ├── 业务行为 - login()/approve()/submit() 等方法         │
│  └── 工厂方法 - admin()/locked()/with_budget() 智能构造   │
├─────────────────────────────────────────────────────────┤
│  L1: 策略层 (Strategy) - 构造与持久化                    │
│  ├── APIStrategy - 调用REST/GraphQL接口（默认）           │
│  ├── DBStrategy - 直接SQL插入（批量/性能）                │
│  ├── HybridStrategy - API头+DB明细（复杂对象）            │
│  └── MockStrategy - 本地内存对象（单元测试）              │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
auto_test/demo_project/
├── api_manager/          # API 管理层 - 统一接口封装
│   ├── __init__.py       # 统一出口 demo_project
│   ├── auth.py           # 认证相关 API
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
│   ├── entities/         # 实体层 - 数据模型定义
│   │   ├── base_entity.py
│   │   ├── user_entity.py
│   │   ├── reimbursement_entity.py
│   │   ├── dept_approval_entity.py
│   │   ├── finance_approval_entity.py
│   │   └── ceo_approval_entity.py
│   │
│   ├── builders/         # 构造器层 - 数据构建与 API 调用
│   │   ├── base_builder.py
│   │   ├── user/
│   │   ├── reimbursement/
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
│   │   ├── base_scenario.py
│   │   ├── auth_scenarios.py
│   │   └── reimbursement_scenarios.py
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
│   │   ├── node.py       # 血缘节点定义
│   │   ├── graph.py      # 血缘图管理
│   │   ├── tracker.py    # 血缘追踪器
│   │   └── analyzer.py   # 血缘分析器
│   │
│   └── variant_matrix/   # 变体矩阵层 - 参数化测试
│       └── variant_matrix.py
│
├── fixtures/             # pytest Fixtures
│   ├── conftest.py       # 全局 Fixture 配置
│   ├── infra/            # 基础设施 Fixtures
│   ├── builders/         # Builder Fixtures
│   └── scenarios/        # Scenario Fixtures
│
├── test_cases/           # 测试用例层
│   ├── base.py           # 测试分层基类
│   ├── test_auth.py      # 认证测试
│   ├── test_user.py      # 用户管理测试
│   ├── test_product.py   # 产品管理测试
│   ├── test_order.py     # 订单管理测试
│   ├── test_reimbursement.py    # 报销申请测试
│   ├── test_dept_approval.py    # 部门审批测试
│   ├── test_finance_approval.py # 财务审批测试
│   ├── test_ceo_approval.py     # CEO审批测试
│   ├── test_approval_workflow.py # 完整审批流测试
│   ├── test_file.py      # 文件上传测试
│   ├── test_data.py      # 数据提交测试
│   ├── test_system.py    # 系统信息测试
│   └── test_new_architecture.py # 新架构演示测试
│
├── examples/             # 示例代码
│   ├── strategy_demo.py          # 策略层演示
│   ├── state_machine_demo.py     # 状态机演示
│   ├── variant_matrix_demo.py    # 变体矩阵演示
│   ├── test_layer_demo.py        # 测试分层演示
│   └── lineage_demo.py           # 血缘追踪演示
│
└── config/               # 配置管理
    ├── settings.py       # 基础配置
    ├── dev.py            # 开发环境
    ├── test.py           # 测试环境
    ├── pre.py            # 预发环境
    └── prod.py           # 生产环境
```

## 核心模块功能说明

### 1. API Manager（接口管理层）

统一封装所有 API 接口，提供统一的调用方式：

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

**支持的 API 模块：**
- **auth** - 用户登录、注册
- **user** - 用户增删改查
- **product** - 产品管理
- **order** - 订单管理
- **reimbursement** - 报销申请（D级模块）
- **dept_approval** - 部门审批（C级模块，依赖D级）
- **finance_approval** - 财务审批（B级模块，依赖C级）
- **ceo_approval** - CEO审批（A级模块，依赖B级）
- **file** - 文件上传
- **data** - 数据提交
- **system** - 健康检查、服务器信息

### 2. Data Factory（数据工厂）

#### 2.1 Entity（实体层）

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

# 检查状态
assert reimbursement.is_pending() is True
```

**实体类型：**
- `UserEntity` - 用户实体
- `ReimbursementEntity` - 报销申请实体
- `DeptApprovalEntity` - 部门审批实体
- `FinanceApprovalEntity` - 财务审批实体
- `CEOApprovalEntity` - CEO审批实体

#### 2.2 Builder（构造器层）

负责构造实体数据并调用 API 创建/更新/删除数据：

```python
from auto_test.demo_project.data_factory.builders import ReimbursementBuilder

# 创建 Builder
builder = ReimbursementBuilder(token="your_token")

# 方式1：构造实体（不调用API）
entity = builder.build(
    user_id=1,
    amount=1000.00,
    reason="测试报销"
)

# 方式2：创建数据（调用API）
reimbursement = builder.create(
    user_id=1,
    amount=1000.00,
    reason="测试报销"
)

# 获取数据
all_reimbursements = builder.get_all()
single = builder.get_by_id(reimbursement.id)

# 更新数据
reimbursement.amount = 1500.00
updated = builder.update(reimbursement)

# 删除数据
builder.delete(reimbursement)
```

**Builder 类型：**
- `UserBuilder` - 用户构造器
- `ReimbursementBuilder` - 报销申请构造器（含 approve/reject 快捷方法）
- `DeptApprovalBuilder` - 部门审批构造器（含 approve/reject 快捷方法）
- `FinanceApprovalBuilder` - 财务审批构造器（含 approve/reject 快捷方法）
- `CEOApprovalBuilder` - CEO审批构造器（含 approve/reject 快捷方法）
- `ProductBuilder` - 产品构造器
- `OrderBuilder` - 订单构造器
- `FileBuilder` - 文件构造器
- `DataBuilder` - 数据构造器
- `SystemBuilder` - 系统构造器

#### 2.3 Scenario（场景层）

封装完整的业务流程，实现复杂测试数据的准备：

```python
from auto_test.demo_project.data_factory.scenarios import FullApprovalWorkflowScenario

# 创建场景
scenario = FullApprovalWorkflowScenario()

# 执行场景 - 自动完成4级审批流程
result = scenario.execute(
    user_id=1,
    amount=5000.00,
    reason="完整审批流程测试"
)

# 获取结果
if result.success:
    reimbursement = result.get_entity("reimbursement")
    dept_approval = result.get_entity("dept_approval")
    finance_approval = result.get_entity("finance_approval")
    ceo_approval = result.get_entity("ceo_approval")
```

**场景类型：**
- `LoginScenario` - 登录场景
- `RegisterAndLoginScenario` - 注册并登录场景
- `CreateReimbursementScenario` - 创建报销申请场景
- `FullApprovalWorkflowScenario` - 完整4级审批流程场景

#### 2.4 Strategy（策略层）

提供多种数据构造策略，支持不同测试场景：

```python
from auto_test.demo_project.data_factory.strategies import (
    APIContextStrategy,
    MockStrategy,
    DBStrategy,
    HybridStrategy,
)

# API策略（默认）- 真实接口调用
api_strategy = APIContextStrategy(api_client)

# Mock策略 - 本地快速测试
mock_strategy = MockStrategy()

# DB策略 - 直接数据库操作
db_strategy = DBStrategy(db_connection)

# Hybrid策略 - API+DB混合
hybrid_strategy = HybridStrategy(api_client, db_connection)
```

**策略类型：**
- `APIContextStrategy` - API调用策略
- `MockStrategy` - Mock数据策略
- `DBStrategy` - 数据库策略
- `HybridStrategy` - 混合策略

#### 2.5 State Machine（状态机层）

实体状态管理，支持状态流转和验证：

```python
from auto_test.demo_project.data_factory.state_machine import UserStateMachine

# 创建状态机
sm = UserStateMachine()

# 定义状态流转
sm.add_transition("active", "locked", "lock")
sm.add_transition("locked", "inactive", "deactivate")
sm.add_transition("active", "inactive", "deactivate")

# 执行状态转换
sm.transition_to("locked")  # active -> locked
sm.transition_to("inactive")  # locked -> inactive

# 获取当前状态
current_state = sm.current_state

# 获取状态历史
history = sm.get_transition_history()
```

**状态机类型：**
- `StateMachine` - 基础状态机
- `UserStateMachine` - 用户状态机

#### 2.6 Lineage（血缘追踪层）

数据血缘自动记录和追踪：

```python
from auto_test.demo_project.data_factory.lineage import DataLineageTracker

# 创建追踪器
tracker = DataLineageTracker()

# 记录数据创建
user_id = tracker.record_creation(
    entity_type="user",
    entity_id="user_001",
    source="api_call",
    metadata={"username": "张三"}
)

# 记录依赖关系
tracker.record_dependency(
    from_entity="order:order_001",
    to_entity="user:user_001",
    relation_type=LineageRelation.DEPENDS_ON
)

# 上游追溯
upstream = tracker.get_upstream("payment:payment_001")

# 下游追溯
downstream = tracker.get_downstream("user:user_001")

# 影响分析
impact = tracker.get_impact_analysis("order:order_001")
```

**血缘功能：**
- `DataLineageNode` - 血缘节点
- `DataLineageGraph` - 血缘图
- `DataLineageTracker` - 血缘追踪器
- `LineageAnalyzer` - 血缘分析器

#### 2.7 Variant Matrix（变体矩阵层）

参数化测试，笛卡尔积自动生成用例：

```python
from auto_test.demo_project.data_factory.scenarios.variant_matrix import (
    VariantMatrix, Dimension, Variant
)

# 定义维度
dimensions = [
    Dimension("user_type", [
        Variant("admin", {"role": "admin"}),
        Variant("normal", {"role": "user"}),
    ]),
    Dimension("amount", [
        Variant("small", {"amount": 100}),
        Variant("large", {"amount": 10000}),
    ]),
]

# 创建变体矩阵
matrix = VariantMatrix(dimensions)

# 生成所有组合（笛卡尔积）
combinations = matrix.generate_combinations()
# 生成: (admin, small), (admin, large), (normal, small), (normal, large)
```

### 3. Fixtures（测试夹具）

提供预配置的测试数据，简化测试用例编写：

```python
# 使用 Fixture 自动创建测试数据
def test_with_reimbursement(created_reimbursement):
    """使用已创建的报销申请进行测试"""
    assert created_reimbursement.id is not None
    assert created_reimbursement.status == "pending"

def test_with_full_workflow(full_approval_workflow):
    """使用完整审批流程进行测试"""
    assert full_approval_workflow["status"] == "fully_approved"
```

**常用 Fixtures：**
- `api_client` - API 客户端（已认证）
- `test_token` - 测试用认证 token
- `test_user` - 测试用户
- `test_product` - 测试产品
- `created_reimbursement` - 已创建的报销申请
- `pending_reimbursement` - 待审批的报销申请
- `dept_approved_reimbursement` - 部门已审批的报销申请
- `finance_approved_reimbursement` - 财务已审批的报销申请
- `ceo_approved_reimbursement` - CEO已审批的报销申请
- `fully_approved_reimbursement` - 完整审批通过的报销申请

### 4. Test Cases（测试用例层）

#### 4.1 测试分层

```python
from auto_test.demo_project.test_cases import UnitTest, IntegrationTest, E2ETest

# 单元测试 - 单接口测试
class TestUserAPI(UnitTest):
    def test_create_user(self):
        result = self.call_api("POST", "/users", {"name": "test"})
        self.assert_success(result)

# 集成测试 - 模块间集成
class TestOrderPayment(IntegrationTest):
    def test_order_creates_payment(self):
        order = self.run_scenario(CreateOrderScenario)
        payment = self.get_related(order, "payment")
        self.assert_consistency(order.amount, payment.amount)

# 端到端测试 - 完整业务流程
class TestApprovalFlow(E2ETest):
    def test_full_approval(self):
        duration = self.measure_performance(
            self.run_business_flow,
            flow=FullApprovalFlow
        )
        self.assert_sla(duration, max_seconds=5)
```

**测试分层类型：**
- `UnitTest` - 单元测试（60%）
- `IntegrationTest` - 集成测试（30%）
- `E2ETest` - 端到端测试（10%）

#### 4.2 数据驱动测试

```python
from auto_test.demo_project.test_cases import case_data

class TestLogin(UnitTest):
    @case_data([
        {"username": "admin", "password": "123456", "expected": "success"},
        {"username": "user", "password": "wrong", "expected": "fail"},
    ])
    def test_login(self, username, password, expected):
        result = self.login(username, password)
        self.assertEqual(result.status, expected)
```

## 执行用例全流程

### 1. 环境准备

#### 1.1 启动 Mock API 服务

```bash
# 进入项目目录
cd d:\code\MangoPytest

# 启动 FastAPI Mock 服务
python service/mock_api.py

# 服务将启动在 http://localhost:8003
```

#### 1.2 安装依赖

```bash
# 使用虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 执行测试用例

#### 2.1 执行所有测试

```bash
# 执行所有测试用例
python -m pytest auto_test/demo_project/test_cases/ -v

# 执行并生成 Allure 报告
python -m pytest auto_test/demo_project/test_cases/ -v --alluredir=./allure-results
```

#### 2.2 执行指定模块测试

```bash
# 执行认证模块测试
python -m pytest auto_test/demo_project/test_cases/test_auth.py -v

# 执行报销申请模块测试
python -m pytest auto_test/demo_project/test_cases/test_reimbursement.py -v

# 执行审批流程测试
python -m pytest auto_test/demo_project/test_cases/test_approval_workflow.py -v
```

#### 2.3 执行指定测试类/方法

```bash
# 执行指定类
python -m pytest auto_test/demo_project/test_cases/test_auth.py::TestAuthLogin -v

# 执行指定方法
python -m pytest auto_test/demo_project/test_cases/test_auth.py::TestAuthLogin::test_login_success -v
```

### 3. 运行示例演示

```bash
# 策略层演示
python auto_test/demo_project/examples/strategy_demo.py

# 状态机演示
python auto_test/demo_project/examples/state_machine_demo.py

# 变体矩阵演示
python auto_test/demo_project/examples/variant_matrix_demo.py

# 测试分层演示
python auto_test/demo_project/examples/test_layer_demo.py

# 血缘追踪演示
python auto_test/demo_project/examples/lineage_demo.py
```

### 4. 测试执行流程详解

#### 4.1 基础模块测试流程（以 test_auth.py 为例）

```
1. 初始化阶段
   └── conftest.py 中的 fixture 执行
       └── api_client: 创建 API 客户端并认证
       └── test_token: 获取认证 token

2. 测试执行阶段
   └── test_login_success
       ├── 调用 demo_project.auth.api_login()
       ├── 验证返回结果
       └── 断言验证

3. 清理阶段
   └── fixture 自动清理
```

#### 4.2 数据工厂测试流程（以 test_reimbursement.py 为例）

```
1. 初始化阶段
   └── conftest.py 中的 fixture 执行
       └── reimbursement_builder: 创建 ReimbursementBuilder 实例

2. 测试执行阶段
   └── test_create_reimbursement
       ├── 调用 reimbursement_builder.build() 构造实体
       ├── 调用 demo_project.reimbursement.create_reimbursement() 创建数据
       ├── 验证返回结果
       └── 断言验证

3. 清理阶段
   └── Builder 自动清理创建的数据
```

#### 4.3 复杂审批流程测试（以 test_approval_workflow.py 为例）

```
1. 初始化阶段
   └── approval_scenarios fixture 执行
       └── 创建 ApprovalScenarios 实例

2. 测试执行阶段
   └── test_full_approval_workflow_scenario
       ├── 调用 approval_scenarios.create_full_approval_workflow()
       │   ├── 创建报销申请（D级）
       │   ├── 部门审批（C级，依赖D级）
       │   ├── 财务审批（B级，依赖C级）
       │   └── CEO审批（A级，依赖B级）
       ├── 验证完整审批流程结果
       └── 断言验证

3. 清理阶段
   └── 各 Builder 自动清理创建的数据
```

### 5. 测试数据流向

```
测试用例 (Test Case)
    ↓ 调用
Fixture（提供预配置数据）
    ↓ 调用
Builder（构造数据 + 调用API）
    ↓ 调用
API Manager（统一接口封装）
    ↓ HTTP 请求
Mock API（模拟后端服务）
    ↓ 返回
API Manager（统一响应处理）
    ↓ 转换
Entity（数据模型）
    ↓ 返回
测试用例（断言验证）
```

### 6. 多级审批依赖关系

本项目演示了4级审批流程的依赖关系：

```
A级模块（CEO审批）
    ↑ 依赖
B级模块（财务审批）
    ↑ 依赖
C级模块（部门审批）
    ↑ 依赖
D级模块（报销申请）
```

**依赖验证规则：**
- 必须先创建报销申请（D级），才能进行部门审批（C级）
- 必须通过部门审批（C级），才能进行财务审批（B级）
- 必须通过财务审批（B级），才能进行CEO审批（A级）
- 任一环节拒绝，流程终止

### 7. 查看测试结果

#### 7.1 控制台输出

```bash
============================= test session starts =============================
platform win32 -- Python 3.10.4, pytest-8.3.3
rootdir: d:\code\MangoPytest
collected 126 items

auto_test/demo_project/test_cases/test_auth.py::TestAuthLogin::test_login_success PASSED
auto_test/demo_project/test_cases/test_auth.py::TestAuthLogin::test_login_wrong_username PASSED
...
============================== 120 passed, 3 skipped, 3 failed in 13.03s ==============================
```

#### 7.2 Allure 报告

```bash
# 生成报告
allure serve ./allure-results

# 或生成静态报告
allure generate ./allure-results -o ./allure-report --clean
```

## 快速开始示例

### 示例1：基础 API 测试

```python
# test_example.py
import pytest
from auto_test.demo_project.api_manager import demo_project

def test_create_user(api_client):
    """测试创建用户"""
    demo_project.user.set_token(api_client.token)
    
    result = demo_project.user.create_user(
        username="test_user",
        email="test@example.com",
        password="Test@123456"
    )
    
    assert result["code"] == 200
    assert result["data"]["username"] == "test_user"
```

### 示例2：使用 Builder 创建测试数据

```python
# test_with_builder.py
import pytest
from auto_test.demo_project.data_factory.builders import ReimbursementBuilder

def test_with_reimbursement(test_token):
    """使用 Builder 创建报销申请"""
    builder = ReimbursementBuilder(token=test_token)
    
    # 创建报销申请
    reimbursement = builder.create(
        user_id=1,
        amount=1000.00,
        reason="差旅报销"
    )
    
    assert reimbursement is not None
    assert reimbursement.id is not None
    assert reimbursement.status == "pending"
    
    # 验证数据
    fetched = builder.get_by_id(reimbursement.id)
    assert fetched.amount == 1000.00
```

### 示例3：使用 Scenario 完成复杂流程

```python
# test_with_scenario.py
import pytest
from auto_test.demo_project.data_factory.scenarios import FullApprovalWorkflowScenario

def test_full_approval_workflow():
    """测试完整4级审批流程"""
    scenario = FullApprovalWorkflowScenario()
    
    result = scenario.execute(
        user_id=1,
        amount=5000.00,
        reason="项目报销"
    )
    
    assert result.success is True
    
    # 验证各级审批
    reimbursement = result.get_entity("reimbursement")
    dept_approval = result.get_entity("dept_approval")
    finance_approval = result.get_entity("finance_approval")
    ceo_approval = result.get_entity("ceo_approval")
    
    assert reimbursement is not None
    assert dept_approval.status == "approved"
    assert finance_approval.status == "approved"
    assert ceo_approval.status == "approved"
```

### 示例4：使用 Fixture 简化测试

```python
# test_with_fixture.py
import pytest

def test_with_approval_workflow(full_approval_workflow):
    """使用 fixture 提供的完整审批流程数据"""
    # full_approval_workflow 是 fixture 自动创建的完整审批数据
    
    assert full_approval_workflow["status"] == "fully_approved"
    assert full_approval_workflow["reimbursement"] is not None
    assert full_approval_workflow["dept_approval"]["status"] == "approved"
    assert full_approval_workflow["finance_approval"]["status"] == "approved"
    assert full_approval_workflow["ceo_approval"]["status"] == "approved"
```

### 示例5：使用策略层

```python
# test_with_strategy.py
from auto_test.demo_project.data_factory.strategies import (
    APIContextStrategy, MockStrategy, HybridStrategy
)
from auto_test.demo_project.data_factory.builders import UserBuilder

def test_with_mock_strategy():
    """使用Mock策略快速测试"""
    strategy = MockStrategy()
    builder = UserBuilder(strategy=strategy)
    
    # 快速创建，不调用真实API
    user = builder.create(username="test")
    assert user.id is not None

def test_with_api_strategy(api_client):
    """使用API策略真实测试"""
    strategy = APIContextStrategy(api_client)
    builder = UserBuilder(strategy=strategy)
    
    # 真实调用API
    user = builder.create(username="test")
    assert user.id is not None
```

### 示例6：使用状态机

```python
# test_with_state_machine.py
from auto_test.demo_project.data_factory.state_machine import UserStateMachine

def test_user_state_transition():
    """测试用户状态流转"""
    sm = UserStateMachine()
    
    # 初始状态
    assert sm.current_state == "active"
    
    # 锁定用户
    sm.transition_to("locked")
    assert sm.current_state == "locked"
    
    # 验证历史
    history = sm.get_transition_history()
    assert len(history) == 1
    assert history[0]["from"] == "active"
    assert history[0]["to"] == "locked"
```

### 示例7：使用变体矩阵

```python
# test_with_variant_matrix.py
from auto_test.demo_project.data_factory.scenarios.variant_matrix import (
    VariantMatrix, Dimension, Variant
)

def test_login_variants():
    """测试登录多变体组合"""
    dimensions = [
        Dimension("user_type", [
            Variant("admin", {"role": "admin"}),
            Variant("normal", {"role": "user"}),
            Variant("locked", {"role": "user", "status": "locked"}),
        ]),
        Dimension("credential", [
            Variant("correct", {"password": "correct"}),
            Variant("wrong", {"password": "wrong"}),
        ]),
    ]
    
    matrix = VariantMatrix(dimensions)
    combinations = matrix.generate_combinations()
    
    # 自动生成6种组合
    assert len(combinations) == 6
```

### 示例8：使用血缘追踪

```python
# test_with_lineage.py
from auto_test.demo_project.data_factory.lineage import DataLineageTracker

def test_data_lineage():
    """测试数据血缘追踪"""
    tracker = DataLineageTracker()
    
    # 记录数据创建
    tracker.record_creation("user", "user_001")
    tracker.record_creation("order", "order_001")
    tracker.record_creation("payment", "payment_001")
    
    # 记录依赖
    tracker.record_dependency("order:order_001", "user:user_001")
    tracker.record_dependency("payment:payment_001", "order:order_001")
    
    # 上游追溯
    upstream = tracker.get_upstream("payment:payment_001")
    assert len(upstream) == 2  # user, order
    
    # 下游追溯
    downstream = tracker.get_downstream("user:user_001")
    assert len(downstream) == 2  # order, payment
```

## 配置说明

### 环境配置

```python
# config/test.py
class TestConfig:
    """测试环境配置"""
    HOST = "http://localhost:8003"
    TIMEOUT = 30
    DEBUG = True
```

### 切换环境

```python
# 设置环境变量
import os
os.environ["ENV"] = "test"  # 或 dev, pre, prod

# 配置管理器会自动加载对应配置
from auto_test.demo_project.config import settings
print(settings.HOST)
```

## 最佳实践

1. **使用 Builder 创建测试数据** - 保证数据一致性，自动处理清理
2. **使用 Fixture 复用测试数据** - 减少重复代码，提高执行效率
3. **使用 Scenario 封装复杂流程** - 提高测试可读性和维护性
4. **使用 Strategy 灵活切换** - API/Mock/DB 按需选择
5. **使用 State Machine 管理状态** - 清晰的状态流转控制
6. **使用 Variant Matrix 参数化** - 全面覆盖组合场景
7. **使用 Lineage 追踪数据** - 快速定位问题根源
8. **分层测试** - 单元测试（快）→ 集成测试（真）→ 端到端测试（全）
9. **数据清理** - 使用 Builder 的上下文管理器或 fixture 的 cleanup

## 注意事项

1. 执行测试前确保 Mock API 服务已启动
2. 使用正确的 Python 虚拟环境
3. 注意 fixture 的依赖关系和执行顺序
4. 审批流程测试需要按顺序执行（D→C→B→A）
5. 使用血缘追踪时注意性能影响（大数据量场景）

## 技术栈

- **Python 3.10+**
- **pytest** - 测试框架
- **requests** - HTTP 客户端
- **pydantic** - 数据验证
- **FastAPI** - Mock API 服务
- **Allure** - 测试报告

## 许可证

MIT License
