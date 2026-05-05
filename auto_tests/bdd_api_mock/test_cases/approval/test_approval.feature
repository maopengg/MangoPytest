# language: zh-CN
# -*- coding: utf-8 -*-
功能: 审批流程管理
  作为审批人
  我希望能够审批报销申请
  以便控制费用支出

  @integration @positive
  场景: 创建部门审批
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "同意报销"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "approval_no"

  @integration @positive
  场景: 获取部门审批列表
    假如 管理员已登录
    当 GET "/dept-approvals"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表

  @integration @positive
  场景: 获取财务审批列表
    假如 管理员已登录
    当 GET "/finance-approvals"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表

  @integration @positive
  场景: 获取总经理审批列表
    假如 管理员已登录
    当 GET "/ceo-approvals"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表

  @negative @boundary
  场景: 创建报销-金额小于等于0
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    当 POST "/reimbursements":
      """
      {
        "user_id": ${{用户.id}},
        "amount": 0,
        "reason": "测试报销"
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @negative @boundary
  场景: 创建报销-原因为空
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    当 POST "/reimbursements":
      """
      {
        "user_id": ${{用户.id}},
        "amount": 1000,
        "reason": ""
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @positive
  场景: 部门审批拒绝
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "rejected",
        "comment": "拒绝报销"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "rejected"

  @negative
  场景: 对已审批申请进行部门审批
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "同意报销"
      }
      """
    那么 响应状态码应该为 200
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "重复审批"
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @integration @positive
  场景: 完整流程-全部通过
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "approved"

  @integration @negative
  场景: 完整流程-部门拒绝
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "rejected",
        "comment": "部门拒绝"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "rejected"

  @integration @positive
  场景: 获取完整审批流程
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    当 GET "/workflow/${{报销.id}}"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "dept_approval"

  @negative
  场景: 更新已审批的报销申请
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "同意报销"
      }
      """
    那么 响应状态码应该为 200
    当 PUT "/reimbursements/${{报销.id}}":
      """
      {
        "user_id": ${{用户.id}},
        "amount": 2000,
        "reason": "更新原因"
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @negative
  场景: 删除有审批记录的报销
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "同意报销"
      }
      """
    那么 响应状态码应该为 200
    当 DELETE "/reimbursements/${{报销.id}}"
    那么 响应字段 "code" 应该为 "400"

  @integration @positive
  场景: 财务审批通过
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "部门审批"
    当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "财务同意",
        "dept_approval_id": ${{部门审批.id}}
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "approved"

  @negative
  场景: 财务审批-部门未通过
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "rejected",
        "comment": "部门拒绝"
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "部门审批"
    当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "财务尝试审批",
        "dept_approval_id": ${{部门审批.id}}
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @integration @positive
  场景: 总经理审批通过
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "部门审批"
    当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "财务同意",
        "dept_approval_id": ${{部门审批.id}}
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "财务审批"
    当 使用 @报销 和 @财务审批 发送 POST 到 "/ceo-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "总经理同意",
        "finance_approval_id": ${{财务审批.id}}
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "approved"

  @negative
  场景: 总经理审批-财务未通过
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "部门审批"
    当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "rejected",
        "comment": "财务拒绝",
        "dept_approval_id": ${{部门审批.id}}
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "财务审批"
    当 使用 @报销 和 @财务审批 发送 POST 到 "/ceo-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "总经理尝试审批",
        "finance_approval_id": ${{财务审批.id}}
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @integration @negative
  场景: 完整流程-财务拒绝
    假如 管理员已登录
    假如 存在"用户" 作为 @用户
    而且 存在"报销" 作为 @报销
    当 使用 @报销 发送 POST 到 "/dept-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "approved",
        "comment": "部门同意"
      }
      """
    那么 响应状态码应该为 200
    当 保存响应字段 "id" 到 "部门审批"
    当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
      """
      {
        "reimbursement_id": ${{报销.id}},
        "approver_id": ${{用户.id}},
        "status": "rejected",
        "comment": "财务拒绝",
        "dept_approval_id": ${{部门审批.id}}
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "rejected"
