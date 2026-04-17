# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘追踪演示
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘追踪演示脚本

展示数据血缘追踪的完整功能：
1. 记录数据创建和依赖
2. 上游/下游追溯
3. 影响分析
4. 血缘可视化
"""

import os
import sys

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 计算 lineage 目录路径 - 使用绝对路径
# 当前目录是 examples，需要向上两级到 bdd_api_mock，然后进入 data_factory/lineage
lineage_dir = os.path.abspath(os.path.join(current_dir, '..', 'data_factory', 'lineage'))

# 将 lineage 目录添加到 Python 路径
sys.path.insert(0, lineage_dir)

# 现在可以直接导入模块
from node import DataLineageNode, LineageEdge, LineageNodeType, LineageRelation
from graph import DataLineageGraph
from tracker import DataLineageTracker, get_global_tracker, reset_global_tracker
from analyzer import LineageAnalyzer


def demo_basic_lineage():
    """演示基础血缘追踪"""
    print("=" * 60)
    print("演示1: 基础血缘追踪")
    print("=" * 60)

    # 创建追踪器
    tracker = DataLineageTracker()

    # 记录数据创建
    user_id = tracker.record_creation(
        entity_type="user",
        entity_id="user_001",
        source="api_call",
        metadata={"username": "张三", "role": "employee"}
    )
    print(f"[OK] 记录用户创建: user_001 (节点ID: {user_id})")

    # 记录订单创建
    order_id = tracker.record_creation(
        entity_type="order",
        entity_id="order_001",
        source="api_call",
        metadata={"amount": 1000, "status": "pending"}
    )
    print(f"[OK] 记录订单创建: order_001 (节点ID: {order_id})")

    # 记录依赖关系：订单依赖用户
    edge_id = tracker.record_dependency(
        from_entity=order_id,
        to_entity=user_id,
        relation_type=LineageRelation.DEPENDS_ON,
        metadata={"relation": "created_by"}
    )
    print(f"[OK] 记录依赖关系: order_001 -> user_001 (边ID: {edge_id})")

    # 记录支付创建
    payment_id = tracker.record_creation(
        entity_type="payment",
        entity_id="payment_001",
        source="api_call",
        metadata={"amount": 1000, "method": "alipay"}
    )
    print(f"[OK] 记录支付创建: payment_001 (节点ID: {payment_id})")

    # 支付依赖订单
    tracker.record_dependency(
        from_entity=payment_id,
        to_entity=order_id,
        relation_type=LineageRelation.DEPENDS_ON
    )
    print(f"[OK] 记录依赖关系: payment_001 -> order_001")

    # 获取统计信息
    stats = tracker.graph.get_statistics()
    print(f"\n血缘图统计:")
    print(f"  - 总节点数: {stats['total_nodes']}")
    print(f"  - 总边数: {stats['total_edges']}")
    print(f"  - 根节点数: {stats['roots']}")
    print(f"  - 叶子节点数: {stats['leaves']}")

    return tracker


def demo_upstream_downstream(tracker: DataLineageTracker):
    """演示上下游追溯"""
    print("\n" + "=" * 60)
    print("演示2: 上下游追溯")
    print("=" * 60)

    # 获取 payment_001 的上游
    upstream = tracker.get_upstream("payment:payment_001")
    print(f"\n[OK] payment_001 的上游依赖:")
    for node in upstream:
        print(f"  - {node.entity_type}:{node.entity_id} (来源: {node.source})")

    # 获取 user_001 的下游
    downstream = tracker.get_downstream("user:user_001")
    print(f"\n[OK] user_001 的下游依赖:")
    for node in downstream:
        print(f"  - {node.entity_type}:{node.entity_id}")

    # 查找路径
    path = tracker.get_lineage_path("user:user_001", "payment:payment_001")
    if path:
        print(f"\n[OK] user_001 到 payment_001 的路径:")
        print(f"  路径长度: {len(path)}")
        for i, node in enumerate(path.nodes):
            print(f"  [{i}] {node.entity_type}:{node.entity_id}")


def demo_api_and_db_tracking():
    """演示API和数据库操作追踪"""
    print("\n" + "=" * 60)
    print("演示3: API和数据库操作追踪")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 记录API调用
    api_node_id = tracker.record_api_call(
        api_name="create_order",
        method="POST",
        endpoint="/api/orders",
        request_data={"user_id": "user_001", "amount": 1000},
        response_data={"order_id": "order_002", "status": "created"}
    )
    print(f"[OK] 记录API调用: POST /api/orders (节点ID: {api_node_id})")

    # 记录数据库操作
    db_node_id = tracker.record_database_operation(
        operation="INSERT",
        table="orders",
        record_id="order_002",
        sql="INSERT INTO orders (id, user_id, amount) VALUES ('order_002', 'user_001', 1000)"
    )
    print(f"[OK] 记录数据库操作: INSERT orders (节点ID: {db_node_id})")

    # 记录实体创建
    entity_id = tracker.record_creation(
        entity_type="order",
        entity_id="order_002",
        source="api_call"
    )
    print(f"[OK] 记录实体创建: order_002")

    return tracker


def demo_operation_context():
    """演示操作上下文追踪"""
    print("\n" + "=" * 60)
    print("演示4: 操作上下文追踪")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 使用上下文管理器追踪操作
    with tracker.trace_operation("create_order_flow") as op_id:
        print(f"[OK] 开始追踪操作: create_order_flow (操作ID: {op_id})")

        # 在上下文中创建的数据会自动关联
        user_id = tracker.record_creation(
            entity_type="user",
            entity_id="user_003",
            metadata={"name": "李四"}
        )
        print(f"  - 自动关联用户创建: user_003")

        order_id = tracker.record_creation(
            entity_type="order",
            entity_id="order_003",
            metadata={"amount": 2000}
        )
        print(f"  - 自动关联订单创建: order_003")

        payment_id = tracker.record_creation(
            entity_type="payment",
            entity_id="payment_003",
            metadata={"amount": 2000}
        )
        print(f"  - 自动关联支付创建: payment_003")

    print(f"[OK] 操作追踪完成")

    # 查看统计
    stats = tracker.graph.get_statistics()
    print(f"\n血缘图统计:")
    print(f"  - 总节点数: {stats['total_nodes']}")
    print(f"  - 总边数: {stats['total_edges']}")


def demo_impact_analysis():
    """演示影响分析"""
    print("\n" + "=" * 60)
    print("演示5: 影响分析")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 构建复杂依赖链
    user_id = tracker.record_creation("user", "user_004")
    order_id = tracker.record_creation("order", "order_004")
    payment_id = tracker.record_creation("payment", "payment_004")
    receipt_id = tracker.record_creation("receipt", "receipt_001")
    invoice_id = tracker.record_creation("invoice", "invoice_001")
    shipment_id = tracker.record_creation("shipment", "shipment_001")

    # 建立依赖关系
    tracker.record_dependency(order_id, user_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(payment_id, order_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(receipt_id, payment_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(invoice_id, payment_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(shipment_id, order_id, LineageRelation.DEPENDS_ON)

    print("[OK] 构建依赖链:")
    print("  user_004 -> order_004 -> payment_004 -> receipt_001")
    print("                         -> invoice_001")
    print("           -> shipment_001")

    # 创建分析器
    analyzer = LineageAnalyzer(tracker.graph)

    # 分析 order_004 的影响
    impact = analyzer.analyze_impact("order", "order_004")
    print(f"\n[OK] order_004 的影响分析:")
    print(f"  - 影响级别: {impact['impact_level']}")
    print(f"  - 下游实体数: {impact['total_downstream']}")
    print(f"  - 建议: {impact['recommendation']}")


def demo_lineage_tracing():
    """演示血缘溯源"""
    print("\n" + "=" * 60)
    print("演示6: 血缘溯源")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 构建多级依赖
    budget_id = tracker.record_creation("budget", "budget_001", metadata={"amount": 10000})
    reimb_id = tracker.record_creation("reimbursement", "reimb_001", metadata={"amount": 1000})
    dept_id = tracker.record_creation("dept_approval", "dept_001", metadata={"status": "approved"})
    finance_id = tracker.record_creation("finance_approval", "finance_001", metadata={"status": "approved"})
    payment_id = tracker.record_creation("payment", "payment_005", metadata={"amount": 1000})

    tracker.record_dependency(reimb_id, budget_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(dept_id, reimb_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(finance_id, dept_id, LineageRelation.DEPENDS_ON)
    tracker.record_dependency(payment_id, finance_id, LineageRelation.DEPENDS_ON)

    print("[OK] 构建审批流依赖链:")
    print("  budget_001 -> reimb_001 -> dept_001 -> finance_001 -> payment_005")

    # 创建分析器
    analyzer = LineageAnalyzer(tracker.graph)

    # 溯源 payment_005
    lineage = analyzer.trace_lineage("payment", "payment_005", direction="upstream")
    print(f"\n[OK] payment_005 的血缘溯源:")
    print(f"  - 上游实体数: {lineage['upstream']['count']}")
    print(f"  - 根来源: {lineage['upstream']['root_sources']}")

    # 查看下游
    lineage = analyzer.trace_lineage("budget", "budget_001", direction="downstream")
    print(f"\n[OK] budget_001 的下游流向:")
    print(f"  - 下游实体数: {lineage['downstream']['count']}")
    print(f"  - 最终消费者: {lineage['downstream']['end_consumers']}")


def demo_visualization():
    """演示可视化导出"""
    print("\n" + "=" * 60)
    print("演示7: 可视化导出")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 构建示例数据
    tracker.record_creation("user", "user_005")
    tracker.record_creation("order", "order_005")
    tracker.record_creation("payment", "payment_006")

    analyzer = LineageAnalyzer(tracker.graph)

    # 生成 Mermaid 图
    mermaid = analyzer.generate_mermaid()
    print("[OK] 生成 Mermaid 流程图:")
    print("-" * 40)
    print(mermaid)
    print("-" * 40)

    # 生成 Graphviz DOT
    dot = analyzer.generate_graphviz()
    print("\n[OK] 生成 Graphviz DOT 格式:")
    print("-" * 40)
    print(dot[:500] + "..." if len(dot) > 500 else dot)
    print("-" * 40)


def demo_advanced_analysis():
    """演示高级分析功能"""
    print("\n" + "=" * 60)
    print("演示8: 高级分析功能")
    print("=" * 60)

    tracker = DataLineageTracker()

    # 构建复杂图
    central_id = tracker.record_creation("user", "central_user")

    # 创建多个下游依赖
    for i in range(8):
        order_id = tracker.record_creation("order", f"order_{i}")
        tracker.record_dependency(order_id, central_id, LineageRelation.DEPENDS_ON)

        # 每个订单再有多个下游
        for j in range(2):
            payment_id = tracker.record_creation("payment", f"payment_{i}_{j}")
            tracker.record_dependency(payment_id, order_id, LineageRelation.DEPENDS_ON)

    analyzer = LineageAnalyzer(tracker.graph)

    # 查找热点
    hotspots = analyzer.find_hotspots(top_n=5)
    print("[OK] 热点数据分析:")
    for i, hotspot in enumerate(hotspots, 1):
        print(f"  {i}. {hotspot['type']}:{hotspot['id']}")
        print(f"     下游依赖数: {hotspot['downstream_count']}")
        print(f"     中心性: {hotspot['centrality']}")

    # 查找孤立数据
    orphaned = analyzer.find_orphaned_data()
    print(f"\n[OK] 孤立数据检查:")
    if orphaned:
        print(f"  发现 {len(orphaned)} 个孤立数据")
    else:
        print(f"  未发现孤立数据")

    # 生成完整报告
    report = analyzer.generate_full_report()
    print(f"\n[OK] 完整报告摘要:")
    print(f"  - 总节点数: {report['summary']['total_nodes']}")
    print(f"  - 总边数: {report['summary']['total_edges']}")
    print(f"  - 热点数: {len(report['hotspots'])}")
    print(f"  - 孤立数据数: {len(report['orphaned_data'])}")
    print(f"  - 循环依赖数: {len(report['cycles'])}")


def demo_global_tracker():
    """演示全局追踪器"""
    print("\n" + "=" * 60)
    print("演示9: 全局追踪器")
    print("=" * 60)

    # 重置全局追踪器
    reset_global_tracker()

    # 获取全局追踪器
    tracker1 = get_global_tracker()
    tracker2 = get_global_tracker()

    print(f"[OK] 获取全局追踪器")
    print(f"  - tracker1 ID: {id(tracker1)}")
    print(f"  - tracker2 ID: {id(tracker2)}")
    print(f"  - 是否为同一实例: {tracker1 is tracker2}")

    # 使用全局追踪器记录数据
    tracker1.record_creation("user", "global_user_001")
    tracker1.record_creation("order", "global_order_001")

    # 通过另一个引用查看数据
    stats = tracker2.graph.get_statistics()
    print(f"\n[OK] 通过 tracker2 查看数据:")
    print(f"  - 总节点数: {stats['total_nodes']}")
    print(f"  - 总边数: {stats['total_edges']}")


def run_all_demos():
    """运行所有演示"""
    print("\n" + "=" * 60)
    print("数据血缘追踪功能演示")
    print("=" * 60)

    # 运行演示
    tracker = demo_basic_lineage()
    demo_upstream_downstream(tracker)
    demo_api_and_db_tracking()
    demo_operation_context()
    demo_impact_analysis()
    demo_lineage_tracing()
    demo_visualization()
    demo_advanced_analysis()
    demo_global_tracker()

    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()
