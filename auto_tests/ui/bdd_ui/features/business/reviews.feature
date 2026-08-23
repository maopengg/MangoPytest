# language: zh-CN
@ui @review @positive
功能: 合同评审

  场景: BDD-UI-REVIEW-001 员工取消进行中的评审
    假如 存在一个进行中的合同评审
    并且 员工已经登录 Mango Mock
    当 员工在评审页面取消该任务
    那么 页面评审状态应该为 "cancelled"
    并且 API 查询到的评审状态应该为 "cancelled"

