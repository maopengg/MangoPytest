      # language: zh-CN
      # -*- coding: utf-8 -*-
      功能: 报销申请管理
      作为员工
      我希望能够提交报销申请
      以便报销费用

      背景:
      假如 用户"testuser"已登录

      @smoke @positive
      场景: 获取所有报销申请列表
      当 GET "/reimbursements"
      那么 响应状态码应该为 200
      而且 响应数据应该是列表

      @smoke @positive
      场景: 创建报销申请
      假如 存在"用户"
      当 使用用户ID POST "/reimbursements":
      """
      {
        "user_id": 1,
        "amount": 1000,
        "reason": "差旅费报销",
        "category": "travel"
      }
      """
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "reimb_no"
      而且 响应数据 "status" 应该为 "pending"

      @positive
      场景: 根据ID获取报销申请
      假如 存在"报销"
      当 使用报销ID GET "/reimbursements?id=${reimbursement.id}"
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "reimb_no"

      @positive
      场景: 更新报销申请
      假如 存在"报销"
      当 使用报销ID PUT "/reimbursements/${reimbursement.id}":
      """
      {
        "user_id": 1,
        "amount": 2000,
        "reason": "更新后的报销原因",
        "category": "travel"
      }
      """
那么 响应状态码应该为 200
而且 响应数据 "amount" 应该为 "2000.0"

@positive
场景: 删除报销申请
假如 存在"报销"
当 使用报销ID DELETE "/reimbursements/${reimbursement.id}"
那么 响应状态码应该为 200
