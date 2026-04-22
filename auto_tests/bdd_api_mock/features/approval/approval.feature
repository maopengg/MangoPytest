# language: zh-CN
# -*- coding: utf-8 -*-
功能: 审批流程管理
  作为审批人
  我希望能够审批报销申请
  以便控制费用支出

  @integration @positive
  场景: 完整的审批流程 - 部门经理审批通过
    假如 存在"报销"
    而且 部门经理已登录
    当 POST "/approvals/dept":
      """
      {"reimbursement_id": ${reimbursement.id}, "status": "approved", "comment": "同意报销"}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "approval_no"

  @integration @positive
  场景: 完整的审批流程 - 财务经理审批通过
    假如 存在"部门审批"
    而且 财务经理已登录
    当 POST "/approvals/finance":
      """
      {"reimbursement_id": ${dept_approval.reimbursement_id}, "dept_approval_id": ${dept_approval.id}, "status": "approved", "comment": "财务审核通过", "finance_check_passed": true}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "approval_no"

  @integration @positive
  场景: 完整的审批流程 - 总经理审批通过
    假如 存在"财务审批"
    而且 总经理已登录
    当 POST "/approvals/ceo":
      """
      {"reimbursement_id": ${finance_approval.reimbursement_id}, "finance_approval_id": ${finance_approval.id}, "status": "approved", "comment": "总经理审批通过"}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "approval_no"

  @integration @positive
  场景: 获取审批日志
    假如 存在"报销"
    当 使用报销ID GET "/approvals/logs/${reimbursement.id}"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表
