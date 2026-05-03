      # language: zh-CN
      # -*- coding: utf-8 -*-
      功能: 订单管理
      作为系统用户
      我希望能够创建和管理订单
      以便购买产品

      背景:
      假如 用户"testuser"已登录

      @smoke @positive
      场景: 获取所有订单列表
      当 GET "/orders"
      那么 响应状态码应该为 200
      而且 响应数据应该是列表

      @smoke @integration @positive
      场景: 创建新订单
      假如 存在"产品"
      当 POST "/orders":
      """
      {
        "product_id": ${product.id},
        "user_id": 1,
        "quantity": 2
      }
      """
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "order_no"
      而且 响应数据应该包含字段 "total_amount"

      @positive
      场景: 根据ID获取指定订单
      假如 存在"订单"
      当 使用订单ID GET "/orders/${order.id}"
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "order_no"

      @positive
      场景: 更新订单状态
      假如 存在"订单"
      当 使用订单ID PUT "/orders/${order.id}":
      """
      {
        "product_id": 1,
        "user_id": 1,
        "quantity": 2,
        "status": "paid"
      }
      """
      那么 响应状态码应该为 200
      而且 响应数据 "status" 应该为 "paid"
