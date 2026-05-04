# language: zh-CN
# -*- coding: utf-8 -*-
功能: 审批流程管理
作为审批人
我希望能够审批报销申请
以便控制费用支出

@integration @positive
场景: 创建部门审批
假如 存在"用户"
而且 存在"报销"
当 使用报销ID POST "/dept-approvals":
"""
{
      "approver_id": 1,
      "status": "approved",
      "comment": "同意报销"
}
"""
那么 响应状态码应该为 200
而且 响应数据应该包含字段 "approval_no"

@integration @positive
场景: 获取部门审批列表
当 GET "/dept-approvals"
那么 响应状态码应该为 200
而且 响应数据应该是列表

@integration @positive
场景: 获取财务审批列表
当 GET "/finance-approvals"
那么 响应状态码应该为 200
而且 响应数据应该是列表

@integration @positive
场景: 获取总经理审批列表
当 GET "/ceo-approvals"
那么 响应状态码应该为 200
而且 响应数据应该是列表
