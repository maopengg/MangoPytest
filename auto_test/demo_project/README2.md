# MangoPytest 企业级自动化测试框架

## 项目概述

MangoPytest 是一个面向企业级应用的自动化测试框架，采用**数据即代码（Data as Code）**设计理念，解决复杂业务系统（如SaaS审批流）的测试数据管理、多环境适配、长流程依赖等核心痛点。

**核心特性**：
- **领域驱动设计**：业务实体封装数据与行为，非静态配置
- **依赖自动解决**：A→B→C→D 链式依赖自动构造，无需手动准备
- **环境自适应**：同一套代码，自动适配 dev/test/prod/ci 环境
- **参数化场景**：业务变体自动生成，笛卡尔积覆盖组合场景
- **全链路追踪**：数据血缘自动记录，故障一键定位

---

## 架构设计

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
MangoPytest/
├── auto_test/                      # 【测试项目目录】
│   └── demo_project/               # 具体项目（可扩展多项目）
│       │
│       ├── config/                 # 【配置中心】环境自适应
│       │   ├── settings.py         # 配置基类 + get_settings()
│       │   ├── dev.py              # 开发环境
│       │   ├── test.py             # 测试环境
│       │   ├── pre.py              # 预发环境
│       │   └── prod.py             # 生产环境（只读）
│       │
│       ├── data_factory/           # 【数据工厂】核心层
│       │   │
│       │   ├── entities/           # 【L2: 实体层】领域对象
│       │   │   ├── base_entity.py  # Entity基类（状态机、追踪）
│       │   │   ├── user_entity.py  # 用户实体（含login行为）
│       │   │   ├── org_entity.py   # 组织实体
│       │   │   ├── budget_entity.py # 预算实体
│       │   │   ├── reimb_entity.py # 报销单实体（含submit/approve）
│       │   │   └── payment_entity.py # 付款单实体
│       │   │
│       │   ├── builders/           # 【构造器】数据创建实现
│       │   │   ├── base_builder.py # Builder基类（依赖解决、清理）
│       │   │   ├── d_module/     # D模块构造器（Org/User）
│       │   │   ├── c_module/     # C模块构造器（Budget）
│       │   │   ├── b_module/     # B模块构造器（Reimbursement）
│       │   │   └── a_module/     # A模块构造器（Payment）
│       │   │
│       │   ├── scenarios/          # 【L3: 场景层】业务流程
│       │   │   ├── base_scenario.py # Scenario基类（变体矩阵）
│       │   │   ├── login_scenario.py # 登录场景（多变体）
│       │   │   ├── reimb_scenario.py # 报销申请场景
│       │   │   └── approval_scenario.py # 完整审批流场景
│       │   │
│       │   └── strategies/         # 【L1: 策略层】构造策略
│       │       ├── base_strategy.py
│       │       ├── api_strategy.py
│       │       ├── db_strategy.py
│       │       └── hybrid_strategy.py
│       │
│       ├── fixtures/               # 【pytest适配层】
│       │   ├── conftest.py         # 全局fixture配置
│       │   ├── infra/              # 基础设施fixtures
│       │   │   ├── client.py       # api_client, db_client
│       │   │   ├── context.py      # test_context（追踪、清理）
│       │   │   └── env.py          # env, settings
│       │   │
│       │   ├── entities/           # 实体fixtures
│       │   │   ├── user_fixtures.py # admin_user, locked_user
│       │   │   └── org_fixtures.py  # default_org
│       │   │
│       │   ├── builders/             # 构造器fixtures
│       │   │   ├── d_fixtures.py   # org_builder, user_builder
│       │   │   ├── c_fixtures.py   # budget_builder
│       │   │   ├── b_fixtures.py   # reimb_builder
│       │   │   └── a_fixtures.py   # payment_builder
│       │   │
│       │   └── scenarios/            # 场景fixtures
│       │       └── approval_fixtures.py # full_approval_scenario
│       │
│       ├── test_cases/             # 【L4: 用例层】
│       │   ├── conftest.py         # 用例层通用配置
│       │   │
│       │   ├── unit/               # 单接口测试（60%）
│       │   │   ├── test_login.py   # 登录接口（多变体）
│       │   │   ├── test_payment_create.py # 付款创建
│       │   │   └── test_payment_validate.py # 付款校验
│       │   │
│       │   ├── integration/          # 模块集成测试（30%）
│       │   │   ├── test_payment_with_reimb.py # A→B真实依赖
│       │   │   └── test_payment_sync.py # 状态同步验证
│       │   │
│       │   └── e2e/                  # 端到端测试（10%）
│       │       └── test_full_approval_flow.py # D→C→B→A全链路
│       │
│       └── utils/                    # 项目工具
│           └── custom_helpers.py
│
├── core/                           # 【框架层】跨项目复用
│   ├── api/                          # 统一API客户端
│   ├── models/                       # 共享数据模型
│   └── utils/                        # 通用工具
│
└── docs/                           # 文档
    ├── architecture.md
    ├── data_factory_guide.md
    └── migration_guide.md
```

---

## 核心设计详解

### 1. 实体层（Entity）- 领域对象

**不是数据容器，是业务概念的代码化**：

```python
# data_factory/entities/user_entity.py

@dataclass
class User(Entity):
    """
    用户实体 - 封装数据、行为、构造工厂
    """
    
    # ========== 领域属性 ==========
    username: str
    password: str = field(repr=False)  # 脱敏
    status: StateMachine["active" → "locked" → "inactive"] = "active"
    role: Literal["admin", "manager", "employee"] = "employee"
    org_id: Optional[str] = None
    
    # ========== 业务行为 ==========
    def login(self, password: str) -> LoginResult:
        """登录行为 - 真实业务逻辑"""
        if self.status == "locked":
            return LoginResult.fail("ACCOUNT_LOCKED")
        if self.password != password:
            self._record_fail()
            return LoginResult.fail("WRONG_PASSWORD")
        return LoginResult.success()
    
    def _record_fail(self):
        """内部行为：记录失败次数，触发锁定"""
        self.fail_count += 1
        if self.fail_count >= 3:
            self.status = "locked"
    
    # ========== 工厂方法 - 智能构造 ==========
    
    @classmethod
    def admin(cls) -> "User":
        """管理员账号 - 环境自适应"""
        settings = get_settings()
        return cls(
            username="admin",
            password=settings.ADMIN_PASSWORD,  # 从环境配置读取
            role="admin",
            status="active"
        )
    
    @classmethod
    def locked(cls) -> "User":
        """
        已锁定用户 - 自动构造前置状态
        不是改字段，而是真的执行3次失败登录
        """
        user = cls.normal()
        user.login("wrong")  # 第1次
        user.login("wrong")  # 第2次
        user.login("wrong")  # 第3次，触发锁定
        return user
    
    @classmethod
    def normal(cls, org_id: Optional[str] = None) -> "User":
        """普通用户 - 随机生成，自动关联组织"""
        return cls(
            username=f"user_{uuid_short()}",
            password="Test@123456",
            role="employee",
            org_id=org_id
        )
```

### 2. 场景层（Scenario）- 业务语义

不是测试用例，是可参数化的业务流程：

```python
# data_factory/scenarios/login_scenario.py

class LoginScenario(Scenario):
    """
    登录场景 - 描述"谁用什么凭证登录"
    支持多变体自动生成
    """
    
    # ========== 依赖声明 ==========
    requires: Dependencies = [User]  # 需要用户实体
    
    # ========== 变体矩阵（笛卡尔积生成用例）==========
    variants = VariantMatrix({
        "actor": {
            "admin": lambda: User.admin(),
            "normal": lambda: User.normal(),
            "locked": lambda: User.locked(),
            "nonexistent": lambda: User.nonexistent(),
        },
        "credential": {
            "correct": lambda user: user.password,
            "wrong": lambda user: user.password + "_wrong",
            "empty": lambda user: "",
        }
    })
    # 自动生成 4×3=12 种组合，自动过滤无效组合
    
    def __init__(self, actor: User, credential: str):
        self.actor = actor
        self.credential = credential
    
    def run(self, strategy: Optional[Strategy] = None) -> LoginResult:
        """执行场景"""
        result = self.actor.login(self.credential, strategy)
        
        return {
            "user": self.actor,
            "credential": self.credential,
            "success": result.success,
            "error_code": result.error_code,
            "expected": self._expected_result()
        }
    
    def _expected_result(self) -> dict:
        """预期结果 - 用于自动断言"""
        if self.actor.status == "nonexistent":
            return {"success": False, "code": "USER_NOT_FOUND"}
        if self.actor.status == "locked":
            return {"success": False, "code": "ACCOUNT_LOCKED"}
        if self.credential != self.actor.password:
            return {"success": False, "code": "WRONG_PASSWORD"}
        return {"success": True, "code": None}
```

#### 复杂场景：多级审批

```python
class FullApprovalScenario(Scenario):
    """
    完整审批流：D(报销) → C(部门) → B(财务) → A(CEO)
    """
    
    requires: Dependencies = [User, Budget]  # 自动准备
    creates: Entities = [Reimbursement, DeptApproval, FinanceApproval, CEOApproval]
    
    variants = {
        "amount": {
            "small": {"reimbursement.amount": 1000},
            "medium": {"reimbursement.amount": 50000},
            "large": {"reimbursement.amount": 500000, "approval.level": 3},
        },
        "urgency": {
            "normal": {"reimbursement.priority": "normal", "sla": 72},
            "urgent": {"reimbursement.priority": "high", "sla": 4},
        }
    }
    
    def orchestrate(self, ctx: Context):
        """编排完整流程"""
        # 1. 准备基础（自动解决依赖）
        submitter = ctx.use(User, role="employee")
        approver_dept = ctx.use(User, role="manager")
        approver_finance = ctx.use(User, role="finance")
        approver_ceo = ctx.use(User, role="ceo")
        budget = ctx.use(Budget, amount__gt=self.params["reimbursement.amount"])
        
        # 2. D级：创建报销
        reimb = ctx.create(Reimbursement,
            applicant=submitter,
            budget=budget,
            **self.params["reimbursement"]
        )
        ctx.action(reimb.submit)
        
        # 3. C级：部门审批
        ctx.action(reimb.approve, by=approver_dept)
        dept_approval = ctx.get_created(DeptApproval)
        
        # 4. B级：财务审批
        ctx.action(reimb.approve, by=approver_finance)
        finance_approval = ctx.get_created(FinanceApproval)
        
        # 5. A级：CEO审批（大额触发）
        if self.params.get("approval.level") >= 3:
            ctx.action(reimb.approve, by=approver_ceo)
            ceo_approval = ctx.get_created(CEOApproval)
        
        return {
            "reimbursement": reimb,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "ceo_approval": ceo_approval if "ceo_approval" in locals() else None,
        }
```

### 3. 构造器层（Builder）- 依赖解决

自动解决 D→C→B→A 依赖链：

```python
# data_factory/builders/a_module/payment_builder.py

class PaymentBuilder(Builder):
    """
    A模块：付款单构造器
    自动解决依赖：Payment → Reimbursement → Budget → Org/User
    """
    
    def __init__(self, api_client, context, parent_builders=None):
        super().__init__(api_client, context)
        # 持有依赖构造器（自动注入）
        self.reimb_builder = self._get_or_create_builder(
            ReimbursementBuilder, parent_builders
        )
    
    def create(
        self,
        reimbursement_id: Optional[str] = None,
        amount: Optional[float] = None,
        auto_prepare_deps: bool = True,
        **overrides
    ) -> PaymentEntity:
        """
        创建付款单
        
        Args:
            reimbursement_id: 报销单ID（不提供则自动创建）
            amount: 金额（不提供则从报销单取）
            auto_prepare_deps: 是否自动准备依赖数据
        """
        # ========== 智能依赖解决 ==========
        if auto_prepare_deps and not reimbursement_id:
            # 自动创建已审批的报销单（触发B→C→D构造）
            reimb = self.reimb_builder.create_approved(
                amount=amount or 1000,
                auto_prepare_deps=True  # 级联自动解决
            )
            reimbursement_id = reimb.id
            amount = amount or reimb.total_amount
        
        # ========== 构造实体 ==========
        payment = PaymentEntity(
            reimbursement_id=reimbursement_id,
            amount=amount,
            status="pending",
            **overrides
        )
        
        # ========== API创建 ==========
        resp = self.api.post("/a-module/payments", payment.to_api_payload())
        payment.id = resp["data"]["id"]
        
        # ========== 追踪清理 ==========
        self.context.track("payment", payment.id, self)
        
        return payment
    
    def delete(self, entity_id: str) -> bool:
        """级联清理"""
        # 先查关联数据
        payment = self.get_by_id(entity_id)
        
        # 清理付款单
        self.api.delete(f"/a-module/payments/{entity_id}")
        
        # 可选：清理上游（根据策略）
        if self.context.cascade_cleanup:
            self.reimb_builder.delete(payment.reimbursement_id)
        
        return True
```

### 4. 用例层（Test Case）- 极致简洁

三种模式，分层使用：

#### 模式1：单接口测试（60%）- Fixture预置数据

```python
# test_cases/unit/test_login.py

class TestLoginUnit:
    """登录接口单元测试"""
    
    @case_data(scenario=LoginScenario.variant("admin", "correct"))
    def test_login_success(self, ctx: TestContext):
        """管理员正确登录"""
        result = ctx.get("result")
        
        assert result["success"] is True
        assert result["user"].role == "admin"
        assert "token" in result
    
    @case_data(scenario=LoginScenario.all_variants())  # 批量12种组合
    def test_login_all_combinations(self, ctx: TestContext):
        """登录全组合覆盖（自动生成12条用例）"""
        result = ctx.get("result")
        expected = result["expected"]
        
        assert result["success"] == expected["success"]
        assert result["error_code"] == expected["code"]
```

#### 模式2：模块集成测试（30%）- 真实依赖

```python
# test_cases/integration/test_payment_with_reimb.py

class TestPaymentIntegration:
    """付款→报销集成测试"""
    
    def test_payment_reads_real_reimbursement(
        self,
        reimb_builder: ReimbursementBuilder,  # 真实构造B数据
        payment_builder: PaymentBuilder
    ):
        """验证付款真实读取报销单数据"""
        # 走真实B流程：创建→提交→审批
        reimb = reimb_builder.create()
        reimb_builder.submit(reimb.id)
        reimb_builder.approve(reimb.id)
        
        # A读取B的真实数据
        payment = payment_builder.create(
            reimbursement_id=reimb.id,
            auto_prepare_deps=False  # 不Mock，用真实的
        )
        
        assert payment.amount == reimb.total_amount
        assert payment.source_status == "approved"
```

#### 模式3：端到端测试（10%）- 完整链路

```python
# test_cases/e2e/test_full_approval_flow.py

class TestApprovalE2E:
    """完整审批流端到端测试"""
    
    @case_data(scenario=FullApprovalScenario.variant("large", "urgent"))
    def test_large_urgent_approval(self, ctx: TestContext):
        """大额紧急审批 - 全链路验证"""
        result = ctx.get("orchestrate_result")
        
        # 验证4级审批完成
        assert result["reimbursement"].status == "fully_approved"
        assert result["dept_approval"].status == "approved"
        assert result["finance_approval"].status == "approved"
        assert result["ceo_approval"].status == "approved"  # 大额触发CEO
        
        # 验证预算扣减
        budget = ctx.get("budget")
        assert budget.used_amount == result["reimbursement"].amount
        
        # 验证SLA预警（紧急）
        assert ctx.event("sla_alert").was_fired(priority="high")
```

---

## 环境管理

### 配置分层

```python
# config/settings.py

class BaseConfig(BaseSettings):
    """配置基类"""
    ENV: str = "dev"
    
    # API
    BASE_URL: str = ""
    TIMEOUT: int = 30
    
    # 数据策略
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = False  # 是否级联清理上游

class DevConfig(BaseConfig):
    """开发环境：快速、调试"""
    BASE_URL = "http://localhost:8080"
    DEFAULT_STRATEGY = CreateStrategy.HYBRID  # 混合加速
    AUTO_CLEANUP = False  # 保留数据调试

class TestConfig(BaseConfig):
    """测试环境：平衡"""
    BASE_URL = "https://test.example.com"
    DEFAULT_STRATEGY = CreateStrategy.API_ONLY  # 真实可靠

class CIConfig(BaseConfig):
    """CI环境：快速、隔离"""
    BASE_URL = "http://ci-server:8080"
    DEFAULT_STRATEGY = CreateStrategy.DB_ONLY  # 极速构造
    AUTO_CLEANUP = True  # 强制清理
```

### 启动指定环境

```bash
# 方式1：命令行（推荐）
pytest --env=prod -m readonly

# 方式2：环境变量（CI/CD）
export TEST_ENV=ci
pytest

# 方式3：pytest.ini默认
[pytest]
env = dev
```

---

## 执行全流程

```bash
# 1. 安装
pip install -r requirements.txt

# 2. 启动依赖服务（如需要）
docker-compose up -d

# 3. 执行测试

# 开发调试 - 快速反馈
pytest --env=dev -xvs test_cases/unit/

# 测试环境 - 全量回归
pytest --env=test --junitxml=report.xml

# 生产监控 - 只读冒烟
pytest --env=prod -m "smoke and readonly"

# CI流水线 - 并行极速
pytest --env=ci -n auto --dist=loadfile

# 4. 查看报告
allure serve ./allure-results
```

---

## 与传统方案对比

| 维度 | 传统Excel/YAML | MangoPytest |
|------|---------------|-------------|
| 数据定义 | 静态配置，无类型检查 | 代码实体，IDE自动补全 |
| 依赖准备 | 手动查ID，复制粘贴 | 自动构造，声明式依赖 |
| 环境适配 | `${变量}`替换，易出错 | 工厂方法，运行时自适应 |
| 参数组合 | 多行复制，维护困难 | 变体矩阵，笛卡尔积生成 |
| 变更追溯 | 文件历史，难定位影响 | Git blame，Code Review |
| 失败调试 | 查日志，人工定位 | 血缘追踪，一键还原现场 |
| 执行速度 | 全API调用，慢 | 策略选择，API/DB/Mock灵活切换 |

---

## 演进路线图

| 阶段 | 时间 | 目标 | 产出 |
|------|------|------|------|
| MVP | 1-2月 | 单模块跑通 | Entity + Builder + 单接口测试 |
| 核心 | 3-4月 | 4级审批流 | Scenario + 依赖自动解决 + 集成测试 |
| 平台 | 5-6月 | 多项目复用 | 框架层抽取，新项目5分钟接入 |
| 智能 | 7-12月 | 自动化生成 | 基于模型自动生成边界值用例 |

---

## 设计原则

1. **数据即代码**：Git版本控制，Code Review，类型安全
2. **声明式依赖**：告诉系统需要什么，而不是怎么构造
3. **环境透明**：同一套代码，自动适配不同环境
4. **分层测试**：单元（快）→ 集成（真）→ 端到端（全）
5. **可追溯**：每个数据知道从哪来、谁创建、为何失败

---

## 许可证

MIT License
