# MangoPytest Demo Project - 数据工厂与自动化测试框架演示

## 项目概述

本项目是一个基于 pytest 的自动化测试框架演示项目，展示了如何使用数据工厂（Data Factory）模式来构建可维护、可扩展的 API 自动化测试。项目采用分层架构设计，包含 Entity、Builder、Scenario 等多个层次，实现了测试数据与测试逻辑的分离。

## 项目架构

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
│   └── strategies/       # 策略层 - 数据构造策略
│       └── base_strategy.py
│
├── fixtures/             # pytest Fixtures
│   ├── conftest.py       # 全局 Fixture 配置
│   ├── infra/            # 基础设施 Fixtures
│   ├── builders/         # Builder Fixtures
│   └── scenarios/        # Scenario Fixtures
│
├── test_cases/           # 测试用例层
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
- `ReimbursementBuilder` - 报销申请构造器
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

### 3. 测试执行流程详解

#### 3.1 基础模块测试流程（以 test_auth.py 为例）

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

#### 3.2 数据工厂测试流程（以 test_reimbursement.py 为例）

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

#### 3.3 复杂审批流程测试（以 test_approval_workflow.py 为例）

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

### 4. 测试数据流向

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

### 5. 多级审批依赖关系

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

### 6. 查看测试结果

#### 6.1 控制台输出

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

#### 6.2 Allure 报告

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
4. **分层测试** - 单元测试（API）→ 集成测试（Builder）→ 端到端测试（Scenario）
5. **数据清理** - 使用 Builder 的上下文管理器或 fixture 的 cleanup

## 注意事项

1. 执行测试前确保 Mock API 服务已启动
2. 使用正确的 Python 虚拟环境
3. 注意 fixture 的依赖关系和执行顺序
4. 审批流程测试需要按顺序执行（D→C→B→A）

## 技术栈

- **Python 3.10+**
- **pytest** - 测试框架
- **requests** - HTTP 客户端
- **pydantic** - 数据验证
- **FastAPI** - Mock API 服务
- **Allure** - 测试报告

## 许可证

MIT License
