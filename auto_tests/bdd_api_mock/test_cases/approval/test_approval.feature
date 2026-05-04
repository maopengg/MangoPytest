# language: zh-CN
# -*- coding: utf-8 -*-
功能: 审批流程管理
作为审批人
我希望能够审批报销申请
以便控制费用支出

@integration @positive
场景: 创建部门审批
假如 存在"用户" 作为 @用户
而且 存在"报销" 作为 @报销
当 使用 @报销 发送 POST 到 "/dept-approvals":
"""
{
      "approver_id": ${{用户.id}},
      "status": "approved",
      "comment": "同意报销"
}
"""
那么 响应状态码应该为 200
而且 响应数据应该包含字段 "approval_no"

@integration @positive
场景: