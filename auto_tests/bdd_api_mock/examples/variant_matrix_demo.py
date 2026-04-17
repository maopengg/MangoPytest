# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 变体矩阵功能演示
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
变体矩阵功能演示

本示例展示：
1. 笛卡尔积生成测试用例
2. 维度定义和约束过滤
3. 变体执行和结果统计
4. 预期结果自动生成
5. 变体分组和过滤
"""

import sys

sys.path.insert(0, r'd:\code\MangoPytest')

from auto_tests.pytest_api_mock.data_factory.scenarios import (
    VariantMatrix,
    Dimension,
    Variant,
    VariantExecutor,
    cartesian_product,
    filter_variants,
    group_variants,
)


def demo_basic_cartesian_product():
    """演示基础笛卡尔积"""
    print("=" * 60)
    print("演示1: 基础笛卡尔积")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user", "guest"]),
        Dimension("action", ["read", "write", "delete"])
    ]

    # 创建变体矩阵
    matrix = VariantMatrix(dimensions)

    # 生成变体
    variants = matrix.generate()

    print(f"维度: {matrix.get_dimension_names()}")
    print(f"生成变体数: {len(variants)}")
    print(f"理论组合数: 3 x 3 = 9")
    print("\n变体列表:")
    for i, variant in enumerate(variants[:5], 1):  # 只显示前5个
        print(f"  {i}. {variant.name}")
    if len(variants) > 5:
        print(f"  ... 还有 {len(variants) - 5} 个")

    return True


def demo_constraint_filtering():
    """演示约束过滤"""
    print("\n" + "=" * 60)
    print("演示2: 约束过滤")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user", "guest"]),
        Dimension("action", ["read", "write", "delete"])
    ]

    # 定义约束（过滤无效组合）
    constraints = [
        # guest 不能 delete
        lambda v: not (v["role"] == "guest" and v["action"] == "delete"),
        # guest 不能 write
        lambda v: not (v["role"] == "guest" and v["action"] == "write"),
    ]

    # 创建带约束的变体矩阵
    matrix = VariantMatrix(dimensions, constraints)

    # 生成变体
    variants = matrix.generate()

    print(f"约束: guest 不能 write/delete")
    print(f"原始组合数: 3 x 3 = 9")
    print(f"过滤后变体数: {len(variants)}")
    print(f"过滤掉: {9 - len(variants)} 个无效组合")

    print("\n有效变体:")
    for variant in variants:
        print(f"  - {variant.name}")

    return True


def demo_variant_execution():
    """演示变体执行"""
    print("\n" + "=" * 60)
    print("演示3: 变体执行")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("amount", [100, 1000, 10000]),
        Dimension("status", ["active", "locked"])
    ]

    # 定义约束
    constraints = [
        # locked 状态不能提交大额报销
        lambda v: not (v["status"] == "locked" and v["amount"] >= 1000)
    ]

    matrix = VariantMatrix(dimensions, constraints)

    # 定义测试函数
    def test_submit_reimbursement(variant: Variant) -> bool:
        """模拟提交报销申请"""
        amount = variant["amount"]
        status = variant["status"]

        # 模拟业务逻辑
        if status == "locked":
            return amount < 1000  # locked 只能提交小额
        return True  # active 可以提交任何金额

    # 定义预期结果生成函数
    def expected_result(variant: Variant) -> dict:
        """生成预期结果"""
        if variant["status"] == "locked" and variant["amount"] >= 1000:
            return {"success": False, "error": "账户已锁定"}
        return {"success": True}

    # 创建执行器
    executor = VariantExecutor(matrix, continue_on_failure=True)

    # 执行所有变体
    result = executor.execute(test_submit_reimbursement, expected_result)

    print(f"总变体数: {result.total}")
    print(f"通过: {result.passed}")
    print(f"失败: {result.failed}")
    print(f"错误: {result.errors}")
    print(f"成功率: {result.success_rate * 100:.1f}%")
    print(f"执行时间: {result.execution_time:.3f}s")

    # 显示失败的变体
    failed_variants = result.get_failed_variants()
    if failed_variants:
        print("\n失败的变体:")
        for v in failed_variants:
            print(f"  - {v.name}: {v.error_message}")

    return True


def demo_expected_result_generation():
    """演示预期结果自动生成"""
    print("\n" + "=" * 60)
    print("演示4: 预期结果自动生成")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user"]),
        Dimension("resource", ["user_data", "system_config"]),
        Dimension("action", ["read", "write"])
    ]

    matrix = VariantMatrix(dimensions)

    # 定义预期结果生成函数
    def generate_expected(variant: Variant) -> dict:
        """根据变体参数生成预期结果"""
        role = variant["role"]
        resource = variant["resource"]
        action = variant["action"]

        # admin 可以读写所有资源
        if role == "admin":
            return {"allowed": True, "reason": "管理员权限"}

        # user 只能读 user_data，不能写 system_config
        if resource == "user_data":
            return {"allowed": True, "reason": "自己的数据"}
        else:  # system_config
            if action == "read":
                return {"allowed": True, "reason": "只读访问"}
            else:  # write
                return {"allowed": False, "reason": "无权限修改系统配置"}

    # 生成变体并打印预期结果
    variants = matrix.generate()

    print(f"生成 {len(variants)} 个测试用例及其预期结果:\n")

    for variant in variants:
        expected = generate_expected(variant)
        status = "允许" if expected["allowed"] else "拒绝"
        print(f"  {variant.name}")
        print(f"    预期: {status} - {expected['reason']}")

    return True


def demo_variant_grouping():
    """演示变体分组"""
    print("\n" + "=" * 60)
    print("演示5: 变体分组")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user"]),
        Dimension("status", ["active", "locked"]),
        Dimension("action", ["read", "write"])
    ]

    matrix = VariantMatrix(dimensions)
    variants = matrix.generate()

    # 按 role 分组
    groups = group_variants(variants, lambda v: v["role"])

    print(f"按 role 分组:")
    for role, role_variants in groups.items():
        print(f"\n  {role} ({len(role_variants)} 个):")
        for v in role_variants[:3]:  # 只显示前3个
            print(f"    - {v.name}")
        if len(role_variants) > 3:
            print(f"    ... 还有 {len(role_variants) - 3} 个")

    return True


def demo_variant_filtering():
    """演示变体过滤"""
    print("\n" + "=" * 60)
    print("演示6: 变体过滤")
    print("=" * 60)

    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user", "guest"]),
        Dimension("action", ["read", "write", "delete"])
    ]

    matrix = VariantMatrix(dimensions)
    variants = matrix.generate()

    print(f"总变体数: {len(variants)}")

    # 过滤出 admin 相关的变体
    admin_variants = filter_variants(variants, lambda v: v["role"] == "admin")
    print(f"admin 相关: {len(admin_variants)} 个")

    # 过滤出 delete 相关的变体
    delete_variants = filter_variants(variants, lambda v: v["action"] == "delete")
    print(f"delete 相关: {len(delete_variants)} 个")

    # 过滤出 admin + delete 的变体
    admin_delete_variants = filter_variants(
        variants,
        lambda v: v["role"] == "admin" and v["action"] == "delete"
    )
    print(f"admin + delete: {len(admin_delete_variants)} 个")

    return True


def demo_cartesian_product_util():
    """演示笛卡尔积工具函数"""
    print("\n" + "=" * 60)
    print("演示7: 笛卡尔积工具函数")
    print("=" * 60)

    # 使用工具函数
    result = cartesian_product([1, 2], ['a', 'b'], [True, False])

    print(f"cartesian_product([1, 2], ['a', 'b'], [True, False])")
    print(f"结果数: {len(result)}")
    print(f"结果:")
    for item in result:
        print(f"  {item}")

    return True


def demo_matrix_statistics():
    """演示矩阵统计信息"""
    print("\n" + "=" * 60)
    print("演示8: 矩阵统计信息")
    print("=" * 60)

    dimensions = [
        Dimension("role", ["admin", "user", "guest"]),
        Dimension("status", ["active", "locked", "inactive"]),
        Dimension("action", ["read", "write", "delete"])
    ]

    constraints = [
        lambda v: not (v["role"] == "guest" and v["action"] == "delete"),
        lambda v: not (v["status"] == "inactive" and v["action"] != "read"),
    ]

    matrix = VariantMatrix(dimensions, constraints)

    stats = matrix.get_statistics()

    print("变体矩阵统计:")
    print(f"  总变体数: {stats['total_variants']}")
    print(f"  维度数: {stats['dimensions']}")
    print(f"  约束数: {stats['constraints']}")
    print(f"  维度详情:")
    for name, count in stats['dimension_details'].items():
        print(f"    - {name}: {count} 个取值")

    # 计算理论组合数
    theoretical = 1
    for dim in dimensions:
        theoretical *= len(dim)
    print(f"\n理论组合数: {theoretical}")
    print(f"实际生成数: {stats['total_variants']}")
    print(f"过滤比例: {(1 - stats['total_variants'] / theoretical) * 100:.1f}%")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Scenario 变体矩阵功能演示")
    print("笛卡尔积自动生成测试用例")
    print("=" * 60)

    results = []

    # 运行所有演示
    results.append(("基础笛卡尔积", demo_basic_cartesian_product()))
    results.append(("约束过滤", demo_constraint_filtering()))
    results.append(("变体执行", demo_variant_execution()))
    results.append(("预期结果生成", demo_expected_result_generation()))
    results.append(("变体分组", demo_variant_grouping()))
    results.append(("变体过滤", demo_variant_filtering()))
    results.append(("笛卡尔积工具", demo_cartesian_product_util()))
    results.append(("矩阵统计", demo_matrix_statistics()))

    # 总结
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)

    for name, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")

    print("\n" + "=" * 60)
    print("变体矩阵特性：")
    print("  - 笛卡尔积自动生成所有参数组合")
    print("  - 约束过滤无效组合")
    print("  - 预期结果自动生成")
    print("  - 变体执行和结果统计")
    print("  - 变体分组和过滤")
    print("  - 执行状态追踪（PENDING/RUNNING/PASSED/FAILED）")
    print("=" * 60)


if __name__ == "__main__":
    main()
