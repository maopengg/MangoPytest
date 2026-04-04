# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态流转图增强器
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
状态流转图增强器

将状态机流转信息可视化到 Allure 报告，包括：
- 状态转换历史
- 当前状态
- 流转统计

使用示例：
    from pe.reporting.enhancers import StateMachineEnhancer
    
    # 附加状态转换历史
    StateMachineEnhancer.attach_state_transitions(state_machine)
"""

from typing import Any, Dict, List, TYPE_CHECKING

from ..adapter import AllureAdapter

if TYPE_CHECKING:
    from auto_test.demo_project.data_factory.state_machine.state_machine import StateMachine


class StateMachineEnhancer:
    """状态流转图增强器"""

    @staticmethod
    def attach_state_transitions(state_machine: "StateMachine"):
        """附加状态转换历史
        
        Args:
            state_machine: 状态机实例
        """
        if not hasattr(state_machine, 'history'):
            return

        # 构建转换历史
        transitions = [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "timestamp": t.timestamp.isoformat() if hasattr(t, 'timestamp') and t.timestamp else None,
                "trigger": getattr(t, 'trigger', None),
                "success": getattr(t, 'success', True)
            }
            for t in state_machine.history
        ]

        data = {
            "current_state": state_machine.current_state,
            "transitions": transitions,
            "total_transitions": len(transitions)
        }

        with AllureAdapter.step("状态转换历史"):
            AllureAdapter.attach_json("状态流转", data)

    @staticmethod
    def attach_state_summary(state_machine: "StateMachine"):
        """附加状态摘要
        
        Args:
            state_machine: 状态机实例
        """
        if not hasattr(state_machine, 'history'):
            return

        # 统计状态访问次数
        state_visits: Dict[str, int] = {}
        for t in state_machine.history:
            state_visits[t.to_state] = state_visits.get(t.to_state, 0) + 1

        summary = {
            "当前状态": state_machine.current_state,
            "总转换次数": len(state_machine.history),
            "状态访问统计": state_visits,
            "访问过的状态": list(state_visits.keys())
        }

        AllureAdapter.attach_json("状态摘要", summary)
