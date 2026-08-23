# language: zh-CN
@ui @claim @positive
功能: 报销审批

  场景: BDD-UI-CLAIM-001 部门经理审批当前节点
    假如 存在一个等待部门经理审批的报销申请
    并且 部门经理已经登录 Mango Mock
    当 部门经理审批当前报销节点
    那么 页面应该进入下一个审批节点
    并且 API 查询到的审批节点应该与页面一致

