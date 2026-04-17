# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试分层功能演示
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
测试分层功能演示

本示例展示：
1. UnitTest - 单元测试层（单接口测试）
2. IntegrationTest - 集成测试层（模块集成）
3. E2ETest - 端到端测试层（完整业务流程）
4. TestContext - 统一测试上下文
5. @case_data - 场景数据绑定装饰器
"""

import sys

sys.path.insert(0, r'd:\code\MangoPytest')


def demo_unit_test():
    """演示单元测试层"""
    print("=" * 60)
    print("演示1: UnitTest - 单元测试层（60%）")
    print("=" * 60)

    print("""
单元测试特点：
  - 单接口测试
  - 最小依赖
  - 快速执行
  - 高覆盖率

使用示例：
    class TestUserAPI(UnitTest):
        def test_create_user_success(self):
            result = self.api.user.create_user(username="test")
            self.assert_success(result)
            self.assert_field_exists(result, "id")
        
        def test_create_user_duplicate(self):
            result = self.api.user.create_user(username="duplicate")
            self.assert_failure(result, expected_code=400)
""")

    # 模拟单元测试
    print("模拟单元测试执行:")
    print("  1. test_create_user_success - [OK] 通过")
    print("  2. test_create_user_duplicate - [OK] 通过")
    print("  3. test_create_user_invalid_params - [OK] 通过")
    print("\n单元测试层: 3 个测试用例全部通过")

    return True


def demo_integration_test():
    """演示集成测试层"""
    print("\n" + "=" * 60)
    print("演示2: IntegrationTest - 集成测试层（30%）")
    print("=" * 60)

    print("""
集成测试特点：
  - 多模块集成
  - 依赖链验证
  - 数据一致性
  - 状态流转

使用示例：
    class TestApprovalWorkflow(IntegrationTest):
        def test_full_approval_flow(self):
            with self.context() as ctx:
                # 创建报销单
                reimb = ctx.create(ReimbursementEntity, amount=1000)
                
                # 部门审批
                ctx.action("dept_approve")
                ctx.expect_status("dept_approved")
                
                # 财务审批
                ctx.action("finance_approve")
                ctx.expect_status("finance_approved")
                
                # CEO审批
                ctx.action("ceo_approve")
                ctx.expect_status("fully_approved")
""")

    # 模拟集成测试
    print("模拟集成测试执行:")
    print("  1. test_full_approval_flow - [OK] 通过")
    print("  2. test_rejection_flow - [OK] 通过")
    print("  3. test_data_consistency - [OK] 通过")
    print("\n集成测试层: 3 个测试用例全部通过")

    return True


def demo_e2e_test():
    """演示端到端测试层"""
    print("\n" + "=" * 60)
    print("演示3: E2ETest - 端到端测试层（10%）")
    print("=" * 60)

    print("""
端到端测试特点：
  - 完整业务流程
  - 真实用户场景
  - 全链路验证
  - 性能关注

使用示例：
    class TestCompleteReimbursementFlow(E2ETest):
        def test_user_submit_to_payment(self):
            with self.context() as ctx:
                # 1. 用户注册
                user = ctx.create(UserEntity, role="employee")
                
                # 2. 提交报销
                reimb = ctx.create(ReimbursementEntity, user_id=user.id)
                ctx.action("submit")
                
                # 3. 完整审批流程
                ctx.run_scenario(FullApprovalWorkflowScenario)
                
                # 4. 验证打款
                ctx.expect_field("payment.status", "completed")
""")

    # 模拟E2E测试
    print("模拟端到端测试执行:")
    print("  1. test_user_submit_to_payment - [OK] 通过 (耗时: 2.3s)")
    print("  2. test_complete_business_flow - [OK] 通过 (耗时: 3.1s)")
    print("\n端到端测试层: 2 个测试用例全部通过")

    return True


def demo_test_context():
    """演示 TestContext 统一测试上下文"""
    print("\n" + "=" * 60)
    print("演示4: TestContext - 统一测试上下文")
    print("=" * 60)

    print("""
TestContext 提供：
  - 数据创建/使用
  - 动作执行
  - 状态验证
  - 事件追踪
  - 自动清理

使用示例：
    with self.context() as ctx:
        # 创建数据
        user = ctx.create(UserEntity, username="test")
        
        # 使用数据
        ctx.use(user)
        
        # 执行动作
        ctx.action("login", username="test", password="123456")
        
        # 验证状态
        ctx.expect_status("active")
        
        # 验证字段
        ctx.expect_field("username", "test")
        
        # 追踪事件
        ctx.event("login_success").was_fired()
""")

    # 演示 TestContext 方法
    print("TestContext 方法列表:")
    print("  - create(entity_type, **kwargs): 创建实体")
    print("  - use(entity): 使用已存在的实体")
    print("  - action(action_name, **params): 执行动作")
    print("  - expect_status(expected_status): 验证状态")
    print("  - expect_field(field_path, expected_value): 验证字段")
    print("  - event(event_name): 事件追踪")
    print("  - cleanup(): 清理数据（上下文退出时自动调用）")

    return True


def demo_case_data_decorator():
    """演示 @case_data 装饰器"""
    print("\n" + "=" * 60)
    print("演示5: @case_data - 场景数据绑定装饰器")
    print("=" * 60)

    print("""
@case_data 装饰器：
  将测试数据绑定到测试方法

使用示例：
    class TestUserAPI(UnitTest):
        @case_data({
            "username": "admin",
            "password": "admin123",
            "expected_role": "admin"
        })
        def test_admin_login(self):
            # 通过 self.case_data 访问绑定的数据
            result = self.api.auth.login(
                self.case_data["username"],
                self.case_data["password"]
            )
            self.assert_success(result)
            self.assert_field_equals(
                result, 
                "data.role", 
                self.case_data["expected_role"]
            )
        
        @case_data({
            "username": "user",
            "password": "user123",
            "expected_role": "user"
        })
        def test_user_login(self):
            result = self.api.auth.login(
                self.case_data["username"],
                self.case_data["password"]
            )
            self.assert_success(result)
""")

    print("@case_data 优势:")
    print("  - 测试数据与测试逻辑分离")
    print("  - 支持数据驱动测试")
    print("  - 便于维护和复用")
    print("  - 清晰的测试意图")

    return True


def demo_test_layer_comparison():
    """演示三层测试对比"""
    print("\n" + "=" * 60)
    print("演示6: 三层测试对比")
    print("=" * 60)

    comparison = """
+------------------+---------------+------------------+------------------+
| 特性             | UnitTest      | IntegrationTest  | E2ETest          |
+------------------+---------------+------------------+------------------+
| 占比             | 60%           | 30%              | 10%              |
| 测试范围         | 单接口        | 多模块集成       | 完整业务流程     |
| 依赖             | 最小          | 中等             | 完整依赖链       |
| 执行速度         | 快            | 中等             | 慢               |
| 稳定性           | 高            | 中等             | 较低             |
| 维护成本         | 低            | 中等             | 高               |
| 发现问题阶段     | 早期          | 中期             | 后期             |
+------------------+---------------+------------------+------------------+

推荐实践：
  1. 优先编写单元测试（快速反馈）
  2. 关键流程编写集成测试（验证集成）
  3. 核心业务流程编写E2E测试（端到端验证）
  4. 保持测试金字塔比例（60:30:10）
"""

    print(comparison)

    return True


def demo_assertion_methods():
    """演示断言方法"""
    print("\n" + "=" * 60)
    print("演示7: 断言方法")
    print("=" * 60)

    print("""
通用断言方法（所有测试层都可用）：

1. assert_success(result, message="")
   断言API调用成功（code == 200）
   
   示例：
       result = self.api.user.create_user(username="test")
       self.assert_success(result)

2. assert_failure(result, expected_code=None, message="")
   断言API调用失败
   
   示例：
       result = self.api.user.create_user(username="")
       self.assert_failure(result, expected_code=400)

3. assert_field_equals(result, field_path, expected_value)
   断言字段值相等（支持路径如 "data.username"）
   
   示例：
       self.assert_field_equals(result, "data.username", "test")
       self.assert_field_equals(result, "data.role", "admin")

4. assert_field_exists(result, field_path)
   断言字段存在（支持路径如 "data.id"）
   
   示例：
       self.assert_field_exists(result, "data.id")
       self.assert_field_exists(result, "data.created_at")
""")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("测试分层架构功能演示")
    print("UnitTest(60%) + IntegrationTest(30%) + E2ETest(10%)")
    print("=" * 60)

    results = []

    # 运行所有演示
    results.append(("UnitTest 单元测试层", demo_unit_test()))
    results.append(("IntegrationTest 集成测试层", demo_integration_test()))
    results.append(("E2ETest 端到端测试层", demo_e2e_test()))
    results.append(("TestContext 统一测试上下文", demo_test_context()))
    results.append(("@case_data 场景数据绑定", demo_case_data_decorator()))
    results.append(("三层测试对比", demo_test_layer_comparison()))
    results.append(("断言方法", demo_assertion_methods()))

    # 总结
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)

    for name, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")

    print("\n" + "=" * 60)
    print("测试分层架构特性：")
    print("  - 三层测试架构（Unit/Integration/E2E）")
    print("  - 统一测试上下文（TestContext）")
    print("  - 场景数据绑定（@case_data）")
    print("  - 丰富的断言方法")
    print("  - 测试结果记录和统计")
    print("  - 支持数据驱动测试")
    print("=" * 60)


if __name__ == "__main__":
    main()
