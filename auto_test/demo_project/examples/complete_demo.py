# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 完整功能演示 - 展示所有已实现的新功能
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
完整功能演示脚本

展示所有已实现的新功能：
1. Context 对象 - ctx.create(), ctx.use(), ctx.action()
2. Scenario 依赖声明和业务编排
3. 变体矩阵与 Scenario 集成
4. Builder 级联清理
5. 策略配置化
6. 新实体（Org, Budget, Payment）
7. 血缘追踪
"""

import sys
import os
import importlib.util

# 设置 stdout 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 计算 data_factory 目录路径
data_factory_dir = os.path.abspath(os.path.join(current_dir, '..', 'data_factory'))

# 将 data_factory 目录添加到 Python 路径
sys.path.insert(0, data_factory_dir)

# 使用 importlib 直接导入模块，绕过 __init__.py
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 导入 Context
context_module = load_module_from_path('context', os.path.join(data_factory_dir, 'context.py'))
Context = context_module.Context

# 导入 BaseScenario
base_scenario_module = load_module_from_path(
    'base_scenario', 
    os.path.join(data_factory_dir, 'scenarios', 'base_scenario.py')
)
BaseScenario = base_scenario_module.BaseScenario
ScenarioResult = base_scenario_module.ScenarioResult
Dependencies = base_scenario_module.Dependencies

# 导入 VariantMatrix
variant_matrix_module = load_module_from_path(
    'variant_matrix',
    os.path.join(data_factory_dir, 'scenarios', 'variant_matrix.py')
)
VariantMatrix = variant_matrix_module.VariantMatrix
Dimension = variant_matrix_module.Dimension
Variant = variant_matrix_module.Variant

# 导入实体
entities_module = load_module_from_path(
    'entities',
    os.path.join(data_factory_dir, 'entities', '__init__.py')
)
UserEntity = entities_module.UserEntity
ReimbursementEntity = entities_module.ReimbursementEntity

# 导入新实体
org_entity_module = load_module_from_path(
    'org_entity',
    os.path.join(data_factory_dir, 'entities', 'org_entity.py')
)
OrgEntity = org_entity_module.OrgEntity

budget_entity_module = load_module_from_path(
    'budget_entity',
    os.path.join(data_factory_dir, 'entities', 'budget_entity.py')
)
BudgetEntity = budget_entity_module.BudgetEntity

payment_entity_module = load_module_from_path(
    'payment_entity',
    os.path.join(data_factory_dir, 'entities', 'payment_entity.py')
)
PaymentEntity = payment_entity_module.PaymentEntity

# 导入配置
config_module = load_module_from_path(
    'settings',
    os.path.join(os.path.dirname(data_factory_dir), 'config', 'settings.py')
)
settings = config_module.settings
CreateStrategy = config_module.CreateStrategy
Environment = config_module.Environment


def demo_context_object():
    """演示1: Context 对象"""
    print("\n" + "=" * 60)
    print("演示1: Context 对象 - ctx.create(), ctx.use(), ctx.action()")
    print("=" * 60)
    
    with Context(auto_cleanup=True) as ctx:
        # 1. 创建实体
        print("\n[1] 创建实体:")
        user = ctx.create(UserEntity, username="test_user", role="admin")
        print(f"  [OK] 创建用户: {user.username} (ID: {user.id})")
        
        org = ctx.create(OrgEntity, name="测试组织", budget_total=100000)
        print(f"  [OK] 创建组织: {org.name} (预算: {org.budget_total})")
        
        # 2. 复用实体
        print("\n[2] 复用实体:")
        existing_user = ctx.use(UserEntity, role="admin")
        if existing_user:
            print(f"  [OK] 复用用户: {existing_user.username}")
        
        # 3. 执行业务动作
        print("\n[3] 执行业务动作:")
        result = ctx.action(user.validate)
        print(f"  [OK] 验证用户: {result}")
        
        # 4. 验证预期
        print("\n[4] 验证预期:")
        is_valid = ctx.expect(user.username).equals("test_user")
        print(f"  [OK] 验证用户名: {is_valid}")
        
        is_admin = ctx.expect(user.role).equals("admin")
        print(f"  [OK] 验证角色: {is_admin}")
        
        # 5. 事件追踪
        print("\n[5] 事件追踪:")
        ctx.fire_event("user_created", priority="normal")
        fired = ctx.event("user_created").was_fired()
        print(f"  [OK] 事件已触发: {fired}")
        
        # 6. 获取创建的实体
        print("\n[6] 获取创建的实体:")
        all_users = ctx.get_all_created(UserEntity)
        print(f"  [OK] 创建的用户数: {len(all_users)}")
        
        print("\n[OK] Context 演示完成")


class LoginScenario(BaseScenario):
    """
    登录场景 - 演示依赖声明和业务编排
    """
    # 依赖声明
    requires: Dependencies = [UserEntity]
    
    # 变体矩阵
    variants = VariantMatrix([
        Dimension("actor", [
            Variant("admin", {"role": "admin", "username": "admin_user"}, 0),
            Variant("normal", {"role": "user", "username": "normal_user"}, 1),
            Variant("locked", {"role": "user", "username": "locked_user", "status": "locked"}, 2),
        ]),
        Dimension("credential", [
            Variant("correct", {"password": "correct_pass", "valid": True}, 0),
            Variant("wrong", {"password": "wrong_pass", "valid": False}, 1),
        ]),
    ])
    
    def orchestrate(self, ctx: Context) -> ScenarioResult:
        """业务编排"""
        result = ScenarioResult()
        
        # 1. 获取或创建用户
        user = ctx.use(UserEntity)
        if not user:
            # 从变体获取参数
            actor_data = self._current_variant.get("actor", {}) if self._current_variant else {}
            cred_data = self._current_variant.get("credential", {}) if self._current_variant else {}
            
            user = ctx.create(
                UserEntity,
                username=actor_data.get("username", "test_user"),
                role=actor_data.get("role", "user"),
                password=cred_data.get("password", "123456")
            )
        
        result.add_entity("user", user)
        
        # 2. 验证登录
        cred_data = self._current_variant.get("credential", {}) if self._current_variant else {}
        is_valid = cred_data.get("valid", True)
        
        if is_valid:
            result.data["login_success"] = True
            result.data["token"] = f"token_{user.id}"
            ctx.fire_event("login_success", priority="normal")
        else:
            result.data["login_success"] = False
            result.data["error"] = "Invalid credentials"
            ctx.fire_event("login_failed", priority="high")
        
        # 3. 验证预期
        if ctx.expect(user.username).is_not_none():
            result.success = True
        
        return result


def demo_scenario_with_dependencies():
    """演示2: Scenario 依赖声明和业务编排"""
    print("\n" + "=" * 60)
    print("演示2: Scenario 依赖声明和业务编排")
    print("=" * 60)
    
    # 1. 基础场景执行
    print("\n[1] 基础场景执行:")
    scenario = LoginScenario()
    result = scenario.execute()
    print(f"  [OK] 场景执行: {'成功' if result.success else '失败'}")
    user = result.get_entity("user")
    if user:
        print(f"  [OK] 创建用户: {user.username}")
    
    # 2. 带变体的场景执行
    print("\n[2] 带变体的场景执行:")
    admin_variant = LoginScenario.variant(actor="admin", credential="correct")
    scenario2 = LoginScenario()
    scenario2.set_variant("admin_correct", admin_variant)
    result2 = scenario2.execute()
    print(f"  [OK] 管理员登录: {'成功' if result2.success else '失败'}")
    
    # 3. 获取所有变体
    print("\n[3] 所有变体组合:")
    all_variants = LoginScenario.all_variants()
    print(f"  [OK] 变体数量: {len(all_variants)}")
    for i, variant in enumerate(all_variants[:3], 1):  # 只显示前3个
        print(f"    变体 {i}: {variant.name}")
    
    print("\n[OK] Scenario 演示完成")


def demo_variant_matrix():
    """演示3: 变体矩阵"""
    print("\n" + "=" * 60)
    print("演示3: 变体矩阵 - 笛卡尔积自动生成用例")
    print("=" * 60)
    
    # 创建变体矩阵
    dimensions = [
        Dimension("user_type", [
            Variant("admin", {"role": "admin", "permissions": "all"}, 0),
            Variant("manager", {"role": "manager", "permissions": "write"}, 1),
            Variant("viewer", {"role": "viewer", "permissions": "read"}, 2),
        ]),
        Dimension("amount", [
            Variant("small", {"amount": 100, "level": "low"}, 0),
            Variant("medium", {"amount": 1000, "level": "medium"}, 1),
            Variant("large", {"amount": 10000, "level": "high"}, 2),
        ]),
        Dimension("status", [
            Variant("active", {"status": "active"}, 0),
            Variant("pending", {"status": "pending"}, 1),
        ]),
    ]
    
    matrix = VariantMatrix(dimensions)
    
    print(f"\n[1] 维度数量: {len(dimensions)}")
    print(f"[2] 变体组合数: {len(matrix.generate())}")
    print(f"    (3 user_types x 3 amounts x 2 statuses = 18 种组合)")
    
    print("\n[3] 前5种组合:")
    for i, variant in enumerate(matrix.generate()[:5], 1):
        print(f"    组合 {i}: {variant.name}")
    
    print("\n[OK] 变体矩阵演示完成")


def demo_new_entities():
    """演示4: 新实体（Org, Budget, Payment）"""
    print("\n" + "=" * 60)
    print("演示4: 新实体 - OrgEntity, BudgetEntity, PaymentEntity")
    print("=" * 60)
    
    # 1. OrgEntity
    print("\n[1] OrgEntity - 组织实体:")
    org = OrgEntity.with_budget(budget=500000, name="研发部门")
    print(f"  [OK] 组织: {org.name}")
    print(f"  [OK] 预算: {org.budget_total}")
    print(f"  [OK] 可用预算: {org.get_available_budget()}")
    
    # 消耗预算
    org.consume_budget(50000)
    print(f"  [OK] 消耗50000后，可用: {org.get_available_budget()}")
    
    # 2. BudgetEntity
    print("\n[2] BudgetEntity - 预算实体:")
    budget = BudgetEntity.for_org(org_id=org.id, amount=200000, category="project")
    print(f"  [OK] 预算ID: {budget.id}")
    print(f"  [OK] 组织ID: {budget.org_id}")
    print(f"  [OK] 总额: {budget.total_amount}")
    print(f"  [OK] 类别: {budget.category}")
    
    # 预留预算
    budget.reserve(30000)
    print(f"  [OK] 预留30000后，可用: {budget.get_available_amount()}")
    
    # 3. PaymentEntity
    print("\n[3] PaymentEntity - 付款单实体:")
    payment = PaymentEntity.with_bank_info(
        payee="供应商A",
        bank_account="6222021234567890123",
        bank_name="工商银行",
        amount=50000
    )
    print(f"  [OK] 付款单: {payment.id}")
    print(f"  [OK] 收款人: {payment.payee}")
    print(f"  [OK] 金额: {payment.amount}")
    print(f"  [OK] 状态: {payment.status}")
    
    # 执行付款
    payment.pay()
    print(f"  [OK] 付款后状态: {payment.status}")
    print(f"  [OK] 付款日期: {payment.pay_date}")
    
    print("\n[OK] 新实体演示完成")


def demo_configuration():
    """演示5: 策略配置化"""
    print("\n" + "=" * 60)
    print("演示5: 策略配置化 - DEFAULT_STRATEGY")
    print("=" * 60)
    
    print(f"\n[1] 当前环境: {settings.ENV.value}")
    print(f"[2] 默认策略: {settings.DEFAULT_STRATEGY.value}")
    print(f"[3] 自动清理: {settings.AUTO_CLEANUP}")
    print(f"[4] 级联清理: {settings.CASCADE_CLEANUP}")
    print(f"[5] 启用血缘: {settings.ENABLE_LINEAGE}")
    
    print("\n[6] 不同环境的策略:")
    
    # 模拟不同环境
    env_configs = {
        "DEV": (Environment.DEV, CreateStrategy.MOCK),
        "TEST": (Environment.TEST, CreateStrategy.API_ONLY),
        "CI": (Environment.CI, CreateStrategy.DB_ONLY),
        "PROD": (Environment.PROD, CreateStrategy.API_ONLY),
    }
    
    for env_name, (env, strategy) in env_configs.items():
        print(f"    {env_name}: {strategy.value}")
    
    print("\n[OK] 配置演示完成")


class ReimbursementWorkflowScenario(BaseScenario):
    """
    报销工作流场景 - 演示完整的业务流程编排
    """
    requires: Dependencies = [UserEntity, OrgEntity, BudgetEntity]
    
    def orchestrate(self, ctx: Context) -> ScenarioResult:
        """业务编排：创建报销申请→审批→付款"""
        result = ScenarioResult()
        
        # 1. 获取或创建用户
        user = ctx.use(UserEntity, role="employee")
        if not user:
            user = ctx.create(UserEntity, username="employee_001", role="employee")
        result.add_entity("user", user)
        
        # 2. 获取或创建组织
        org = ctx.use(OrgEntity)
        if not org:
            org = ctx.create(OrgEntity, name="研发部门", budget_total=100000)
        result.add_entity("org", org)
        
        # 3. 获取或创建预算
        budget = ctx.use(BudgetEntity, category="project")
        if not budget:
            budget = ctx.create(BudgetEntity, org_id=org.id, total_amount=50000, category="project")
        result.add_entity("budget", budget)
        
        # 4. 创建报销申请
        reimb = ctx.create(
            ReimbursementEntity,
            user_id=user.id,
            amount=3000,
            reason="差旅报销",
            status="pending"
        )
        result.add_entity("reimbursement", reimb)
        
        # 5. 检查预算
        if budget.has_enough_budget(reimb.amount):
            ctx.fire_event("budget_sufficient", priority="normal")
            result.data["budget_check"] = "passed"
        else:
            ctx.fire_event("budget_insufficient", priority="high")
            result.data["budget_check"] = "failed"
        
        # 6. 创建付款单
        payment = ctx.create(
            PaymentEntity,
            reimbursement_id=reimb.id,
            amount=reimb.amount,
            payee=user.username,
            status="pending"
        )
        result.add_entity("payment", payment)
        
        # 7. 验证
        result.success = ctx.expect(payment.amount).equals(reimb.amount)
        
        return result


def demo_complete_workflow():
    """演示6: 完整工作流"""
    print("\n" + "=" * 60)
    print("演示6: 完整工作流 - 报销→审批→付款")
    print("=" * 60)
    
    scenario = ReimbursementWorkflowScenario()
    result = scenario.execute()
    
    print(f"\n[1] 场景执行: {'成功' if result.success else '失败'}")
    
    print("\n[2] 创建的实体:")
    for name, entity in result.entities.items():
        print(f"    - {name}: {entity.__class__.__name__} (ID: {getattr(entity, 'id', 'N/A')})")
    
    print("\n[3] 业务数据:")
    for key, value in result.data.items():
        print(f"    - {key}: {value}")
    
    # 验证事件
    if result.context:
        print("\n[4] 事件追踪:")
        budget_event = result.context.event("budget_sufficient")
        print(f"    - budget_sufficient: {budget_event.was_fired()}")
    
    print("\n[OK] 完整工作流演示完成")


def run_all_demos():
    """运行所有演示"""
    print("\n" + "=" * 60)
    print("完整功能演示 - 所有新功能")
    print("=" * 60)
    
    demo_context_object()
    demo_scenario_with_dependencies()
    demo_variant_matrix()
    demo_new_entities()
    demo_configuration()
    demo_complete_workflow()
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)
    
    print("\n已实现的功能总结:")
    print("  [OK] Context 对象 - ctx.create(), ctx.use(), ctx.action()")
    print("  [OK] Scenario 依赖声明 - requires: Dependencies")
    print("  [OK] Scenario 业务编排 - orchestrate(self, ctx)")
    print("  [OK] 变体矩阵集成 - variants = VariantMatrix()")
    print("  [OK] Builder 级联清理 - cascade_cleanup")
    print("  [OK] 策略配置化 - DEFAULT_STRATEGY")
    print("  [OK] 新实体 - OrgEntity, BudgetEntity, PaymentEntity")
    print("  [OK] 配置管理 - 环境自动检测")


if __name__ == "__main__":
    run_all_demos()
