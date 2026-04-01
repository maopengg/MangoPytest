# README.md 与 README2.md 功能对比分析报告

## 概述

本报告对比了当前实现的 README.md 与设计文档 README2.md，分析已实现功能和待实现功能。

---

## 已实现功能 ✅

### 1. 核心架构层

| 层级 | 功能 | 实现状态 |
|------|------|----------|
| L1: Strategy（策略层） | API/Mock/DB/Hybrid 策略 | ✅ 已实现 |
| L2: Entity（实体层） | 领域对象定义 | ✅ 已实现 |
| L2: State Machine（状态机） | 实体状态管理 | ✅ 已实现 |
| L3: Scenario（场景层） | 业务流程封装 | ✅ 已实现 |
| L3: Variant Matrix（变体矩阵） | 参数化组合生成 | ✅ 已实现 |
| L4: Test Case（用例层） | 单元/集成/E2E测试分层 | ✅ 已实现 |
| Lineage（血缘追踪） | 数据血缘自动记录 | ✅ 已实现 |

### 2. 已实现的核心功能

1. **策略层（Strategy）**
   - ✅ APIContextStrategy - API调用策略
   - ✅ MockStrategy - Mock数据策略
   - ✅ DBStrategy - 数据库策略
   - ✅ HybridStrategy - 混合策略

2. **实体层（Entity）**
   - ✅ UserEntity - 用户实体
   - ✅ ReimbursementEntity - 报销申请实体
   - ✅ DeptApprovalEntity - 部门审批实体
   - ✅ FinanceApprovalEntity - 财务审批实体
   - ✅ CEOApprovalEntity - CEO审批实体

3. **状态机（State Machine）**
   - ✅ StateMachine - 基础状态机基类
   - ✅ UserStateMachine - 用户状态机（active→locked→inactive）
   - ✅ 状态转换历史记录
   - ✅ 转换钩子（hooks）

4. **变体矩阵（Variant Matrix）**
   - ✅ VariantMatrix - 变体矩阵
   - ✅ Dimension - 维度定义
   - ✅ Variant - 变体定义
   - ✅ 笛卡尔积自动生成组合

5. **测试分层（Test Layer）**
   - ✅ UnitTest - 单元测试基类（60%）
   - ✅ IntegrationTest - 集成测试基类（30%）
   - ✅ E2ETest - 端到端测试基类（10%）
   - ✅ TestContext - 统一测试上下文
   - ✅ @case_data - 数据驱动装饰器

6. **血缘追踪（Lineage）**
   - ✅ DataLineageNode - 血缘节点
   - ✅ DataLineageGraph - 血缘图
   - ✅ DataLineageTracker - 血缘追踪器
   - ✅ LineageAnalyzer - 血缘分析器
   - ✅ 上游/下游追溯
   - ✅ 影响分析
   - ✅ 可视化导出（Mermaid/Graphviz）

---

## 缺失功能分析 ⚠️

### 1. 实体层（Entity）缺失

| 缺失实体 | 说明 | 优先级 |
|----------|------|--------|
| OrgEntity | 组织实体 | 中 |
| BudgetEntity | 预算实体 | 中 |
| PaymentEntity | 付款单实体 | 中 |

**README2.md 中的设计：**
```python
@dataclass
class User(Entity):
    org_id: Optional[str] = None  # 需要 OrgEntity
    
    @classmethod
    def normal(cls, org_id: Optional[str] = None) -> "User":
        """普通用户 - 随机生成，自动关联组织"""
        return cls(
            username=f"user_{uuid_short()}",
            password="Test@123456",
            role="employee",
            org_id=org_id  # 需要 OrgEntity 支持
        )
```

### 2. Builder 层缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| 级联清理（cascade_cleanup） | Builder 自动清理上游依赖数据 | 高 |
| 智能依赖注入 | `_get_or_create_builder` 自动注入 | 中 |
| 策略自动选择 | 根据环境自动选择策略 | 中 |

**README2.md 中的设计：**
```python
class PaymentBuilder(Builder):
    def __init__(self, api_client, context, parent_builders=None):
        super().__init__(api_client, context)
        # 持有依赖构造器（自动注入）
        self.reimb_builder = self._get_or_create_builder(
            ReimbursementBuilder, parent_builders
        )
    
    def delete(self, entity_id: str) -> bool:
        """级联清理"""
        if self.context.cascade_cleanup:
            self.reimb_builder.delete(payment.reimbursement_id)
```

### 3. Scenario 层缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| 依赖声明（Dependencies） | `requires: Dependencies = [User]` | 高 |
| 变体矩阵集成 | `variants = VariantMatrix({...})` | 高 |
| 业务编排（Orchestrate） | `orchestrate(self, ctx: Context)` | 高 |
| 预期结果自动断言 | `_expected_result()` | 中 |
| Context 对象 | `ctx.create()`, `ctx.use()`, `ctx.action()` | 高 |

**README2.md 中的设计：**
```python
class LoginScenario(Scenario):
    requires: Dependencies = [User]  # 需要用户实体
    
    variants = VariantMatrix({  # 变体矩阵
        "actor": {
            "admin": lambda: User.admin(),
            "normal": lambda: User.normal(),
            "locked": lambda: User.locked(),
        },
        "credential": {...}
    })
    
    def orchestrate(self, ctx: Context):  # 业务编排
        submitter = ctx.use(User, role="employee")
        budget = ctx.use(Budget, amount__gt=self.params["amount"])
        reimb = ctx.create(Reimbursement, applicant=submitter)
        ctx.action(reimb.submit)
```

### 4. 配置层缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| 策略配置 | `DEFAULT_STRATEGY: CreateStrategy` | 中 |
| 清理配置 | `AUTO_CLEANUP`, `CASCADE_CLEANUP` | 中 |
| 环境自动检测 | `ENV` 自动检测 | 低 |
| CI 环境配置 | `CIConfig` | 低 |

**README2.md 中的设计：**
```python
class BaseConfig(BaseSettings):
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = False

class CIConfig(BaseConfig):
    DEFAULT_STRATEGY = CreateStrategy.DB_ONLY  # 极速构造
    AUTO_CLEANUP = True  # 强制清理
```

### 5. 测试用例层缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| 测试目录分层 | `unit/`, `integration/`, `e2e/` 子目录 | 低 |
| 场景变体自动展开 | `@case_data(scenario=LoginScenario.all_variants())` | 高 |
| 预期结果自动比较 | `assert result["success"] == expected["success"]` | 中 |
| SLA 验证 | `ctx.event("sla_alert").was_fired(priority="high")` | 中 |

**README2.md 中的设计：**
```python
# test_cases/unit/test_login.py
class TestLoginUnit:
    @case_data(scenario=LoginScenario.variant("admin", "correct"))
    def test_login_success(self, ctx: TestContext):
        result = ctx.get("result")
        assert result["success"] is True
    
    @case_data(scenario=LoginScenario.all_variants())  # 批量12种组合
    def test_login_all_combinations(self, ctx: TestContext):
        result = ctx.get("result")
        expected = result["expected"]
        assert result["success"] == expected["success"]
```

### 6. Fixtures 层缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| 实体 Fixtures | `admin_user`, `locked_user` | 中 |
| 构造器 Fixtures | 按模块分层（d_fixtures, c_fixtures等） | 低 |
| test_context | 追踪、清理上下文 | 高 |

**README2.md 中的设计：**
```python
# fixtures/infra/context.py
test_context（追踪、清理）

# fixtures/entities/user_fixtures.py
admin_user, locked_user

# fixtures/builders/d_fixtures.py
org_builder, user_builder
```

### 7. 框架层（Core）缺失

| 缺失功能 | 说明 | 优先级 |
|----------|------|--------|
| core/ 目录 | 跨项目复用的框架层 | 低 |
| 统一API客户端 | `core/api/` | 中 |
| 共享数据模型 | `core/models/` | 中 |

**README2.md 中的设计：**
```
core/                           # 【框架层】跨项目复用
├── api/                          # 统一API客户端
├── models/                       # 共享数据模型
└── utils/                        # 通用工具
```

---

## 功能优先级排序

### 🔴 高优先级（核心功能缺失）

1. **Scenario 依赖声明与自动解决** - `requires: Dependencies = [User]`
2. **Scenario 业务编排** - `orchestrate(self, ctx: Context)`
3. **Context 对象** - `ctx.create()`, `ctx.use()`, `ctx.action()`
4. **变体矩阵与 Scenario 集成** - `variants = VariantMatrix({...})`
5. **Builder 级联清理** - `cascade_cleanup`
6. **test_context Fixture** - 追踪和清理上下文

### 🟡 中优先级（增强功能）

7. **OrgEntity / BudgetEntity / PaymentEntity** - 缺失的实体
8. **Builder 智能依赖注入** - `_get_or_create_builder()`
9. **策略配置化** - `DEFAULT_STRATEGY`
10. **场景变体自动展开** - `@case_data(scenario.all_variants())`
11. **预期结果自动断言** - `_expected_result()`

### 🟢 低优先级（优化功能）

12. **CI 环境配置** - `CIConfig`
13. **测试目录分层** - `unit/`, `integration/`, `e2e/`
14. **Fixtures 分层** - `d_fixtures`, `c_fixtures` 等
15. **core/ 框架层** - 跨项目复用
16. **SLA 验证** - `sla_alert.was_fired()`

---

## 建议实现顺序

### 第一阶段：核心流程打通
1. 实现 `Context` 类 - 支持 `create()`, `use()`, `action()`
2. 增强 `Scenario` 基类 - 支持 `requires` 和 `orchestrate()`
3. 集成 `VariantMatrix` 到 `Scenario`

### 第二阶段：数据完整性
4. 实现 `OrgEntity`, `BudgetEntity`
5. 实现 `Builder` 级联清理
6. 实现 `test_context` Fixture

### 第三阶段：测试体验优化
7. 实现 `@case_data` 的场景变体自动展开
8. 实现预期结果自动断言
9. 配置策略化

### 第四阶段：工程化
10. 创建 `core/` 框架层
11. 完善 CI/CD 配置
12. 文档和示例完善

---

## 总结

### 已实现（约 60%）
- ✅ 基础架构四层设计
- ✅ 策略层（4种策略）
- ✅ 实体层（5个实体）
- ✅ 状态机
- ✅ 变体矩阵
- ✅ 测试分层
- ✅ 血缘追踪

### 待实现（约 40%）
- ⚠️ Scenario 依赖声明与编排
- ⚠️ Context 对象
- ⚠️ Builder 级联清理
- ⚠️ 场景变体自动展开
- ⚠️ 部分实体（Org, Budget, Payment）
- ⚠️ 配置策略化
- ⚠️ core/ 框架层

**当前框架已经具备了核心能力，可以完成基本的测试数据构造和业务流程测试。建议优先实现 Scenario 的依赖声明和编排功能，这将大大提升复杂业务流程测试的编写效率。**
