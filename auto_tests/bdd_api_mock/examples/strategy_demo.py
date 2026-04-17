# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Strategy层和Builder自动依赖解决功能演示
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
Strategy层和Builder增强功能演示

本示例展示：
1. 四种策略的使用（API/Mock/DB/Hybrid）
2. Builder的自动依赖解决
3. 级联构造（D→C→B→A）
4. 级联清理
"""

import sys

sys.path.insert(0, r"d:\code\MangoPytest")

from auto_tests.bdd_api_mock.data_factory.strategies import (
    APIStrategy,
    MockStrategy,
    DBStrategy,
)
from auto_tests.bdd_api_mock.data_factory.builders import (
    BuilderContext,
    ReimbursementBuilder,
)
from auto_tests.bdd_api_mock.data_factory.entities import ReimbursementEntity


def demo_api_strategy():
    """演示API策略"""
    print("=" * 60)
    print("演示1: API策略（调用真实API）")
    print("=" * 60)

    # 创建API策略（需要token）
    # 注意：实际使用时需要有效的token
    strategy = APIStrategy(token="demo_token")

    # 创建实体
    result = strategy.create(
        ReimbursementEntity, user_id=1, amount=1000.00, reason="API策略测试"
    )

    if result.success:
        print(f"[OK] 创建成功: ID={result.entity.id}")
    else:
        print(f"[FAIL] 创建失败: {result.error_code} - {result.error_message}")

    return result.success


def demo_mock_strategy():
    """演示Mock策略"""
    print("\n" + "=" * 60)
    print("演示2: Mock策略（内存对象，无需API）")
    print("=" * 60)

    # 创建Mock策略（无需token，无需真实API）
    strategy = MockStrategy()

    # 创建多个实体
    for i in range(3):
        result = strategy.create(
            ReimbursementEntity,
            user_id=i + 1,
            amount=100.00 * (i + 1),
            reason=f"Mock测试-{i}",
        )

        if result.success:
            print(
                f"[OK] 创建成功: ID={result.entity.id}, Amount={result.entity.amount}"
            )

    # 查询所有
    all_entities = strategy.get_all(ReimbursementEntity)
    print(f"  内存中共有 {len(all_entities)} 个实体")

    # 清理
    strategy.clear(ReimbursementEntity)
    print(f"  清理后: {strategy.count(ReimbursementEntity)} 个实体")

    return True


def demo_db_strategy():
    """演示DB策略"""
    print("\n" + "=" * 60)
    print("演示3: DB策略（直接SQL，批量操作）")
    print("=" * 60)

    # 创建DB策略（需要数据库配置）
    db_config = {
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "user": "root",
        "password": "password",
    }
    strategy = DBStrategy(db_config=db_config)

    # 批量创建
    data_list = [
        {"user_id": 1, "amount": 100.00, "reason": "批量-1"},
        {"user_id": 2, "amount": 200.00, "reason": "批量-2"},
        {"user_id": 3, "amount": 300.00, "reason": "批量-3"},
    ]

    result = strategy.batch_create(ReimbursementEntity, data_list)

    if result.success:
        print(f"[OK] 批量创建成功: {len(result.entities)} 个实体")
        for entity in result.entities:
            print(f"  - ID={entity.id}")

    return result.success


def demo_builder_with_strategy():
    """演示Builder集成Strategy"""
    print("\n" + "=" * 60)
    print("演示4: Builder集成Strategy")
    print("=" * 60)

    # 方式1：使用API策略（默认）
    print("  方式1: API策略")
    api_context = BuilderContext(
        strategy=APIStrategy(token="demo_token"), auto_prepare_deps=True
    )
    api_builder = ReimbursementBuilder(token="demo_token", context=api_context)
    print(f"  - Builder策略: {api_builder.context.strategy.__class__.__name__}")

    # 方式2：使用Mock策略（单元测试）
    print("  方式2: Mock策略")
    mock_context = BuilderContext(strategy=MockStrategy(), auto_prepare_deps=True)
    mock_builder = ReimbursementBuilder(context=mock_context)
    print(f"  - Builder策略: {mock_builder.context.strategy.__class__.__name__}")

    # 使用Mock策略创建（不调用真实API）
    result = mock_builder.create(user_id=1, amount=500.00, reason="Builder+Mock测试")

    if result:
        print(f"[OK] 创建成功: ID={result.id}")

    return True


def demo_cascade_cleanup():
    """演示级联清理"""
    print("\n" + "=" * 60)
    print("演示5: 级联清理")
    print("=" * 60)

    # 创建启用级联清理的上下文
    context = BuilderContext(
        strategy=MockStrategy(),
        cascade_cleanup=True,  # 启用级联清理
        auto_prepare_deps=True,
    )

    builder = ReimbursementBuilder(context=context)

    # 创建数据
    print("  创建数据...")
    entity = builder.create(user_id=1, amount=1000.00, reason="级联清理测试")

    if entity:
        print(f"  - 创建: ID={entity.id}")
        print(f"  - 已追踪实体数: {len(builder.get_created_entities())}")

    # 使用上下文管理器自动清理
    print("  执行清理...")
    builder.cleanup()
    print("[OK] 清理完成")

    return True


def demo_builder_context_tracking():
    """演示Builder上下文追踪"""
    print("\n" + "=" * 60)
    print("演示6: Builder上下文追踪")
    print("=" * 60)

    # 创建共享上下文
    shared_context = BuilderContext(strategy=MockStrategy())

    # 多个Builder共享同一个上下文
    builder1 = ReimbursementBuilder(context=shared_context)

    # 创建数据
    entity1 = builder1.create(user_id=1, amount=100.00, reason="追踪-1")
    entity2 = builder1.create(user_id=2, amount=200.00, reason="追踪-2")

    # 查看上下文追踪的数据
    all_created = shared_context.get_all_created()
    print(f"  上下文追踪的所有实体:")
    for entity_type, items in all_created.items():
        print(f"    - {entity_type}: {len(items)} 个")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Strategy层和Builder增强功能演示")
    print("=" * 60)

    results = []

    # 运行所有演示
    results.append(("API策略", demo_api_strategy()))
    results.append(("Mock策略", demo_mock_strategy()))
    results.append(("DB策略", demo_db_strategy()))
    results.append(("Builder+Strategy", demo_builder_with_strategy()))
    results.append(("级联清理", demo_cascade_cleanup()))
    results.append(("上下文追踪", demo_builder_context_tracking()))

    # 总结
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)

    for name, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")

    print("\n" + "=" * 60)
    print("提示：")
    print("  - API策略需要启动Mock API服务（python service/mock_api.py）")
    print("  - DB策略需要真实数据库连接配置")
    print("  - Mock策略无需任何外部依赖，适合单元测试")
    print("=" * 60)


if __name__ == "__main__":
    main()
