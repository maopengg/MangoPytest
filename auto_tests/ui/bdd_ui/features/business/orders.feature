# language: zh-CN
@ui @order
功能: 订单支付和退款

  @smoke @positive
  场景: BDD-UI-ORDER-001 员工支付待支付订单
    假如 存在一个属于当前员工的待支付订单
    并且 员工已经登录 Mango Mock
    当 员工在订单页面支付该订单
    那么 页面订单状态应该为 "paid"
    并且 API 查询到的订单状态应该为 "paid"

  @positive
  场景: BDD-UI-ORDER-002 员工退款已支付订单
    假如 存在一个属于当前员工的已支付订单
    并且 员工已经登录 Mango Mock
    当 员工在订单页面退款该订单
    那么 页面订单状态应该为 "refunded"
    并且 API 查询到的订单状态应该为 "refunded"

