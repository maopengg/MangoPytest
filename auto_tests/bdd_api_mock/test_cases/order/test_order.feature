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
      假如 存在"产品" 作为 @产品
      当 POST "/orders":
      """
      {
      "product_id": ${{产品.id}},
      "user_id": 1,
      "quantity": 2
      }
      """
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "order_no"
      而且 响应数据应该包含字段 "total_amount"

      @positive
      场景: 根据ID获取指定订单
      假如 存在"订单" 作为 @订单
      当 GET "/orders/${{订单.id}}"
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "order_no"

      @positive
      场景: 更新订单状态
      假如 存在"订单" 作为 @订单
      当 PUT "/orders/${{订单.id}}":
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

      @positive
      场景: 删除订单
      假如 存在"订单" 作为 @订单
      当 DELETE "/orders/${{订单.id}}"
      那么 响应状态码应该为 200

      @negative
      场景: 创建订单-产品不存在
      当 POST "/orders":
      """
      {
        "product_id": 99999,
        "user_id": 1,
        "quantity": 2
      }
      """
      那么 响应字段 "code" 应该为 "404"

      @negative @boundary
      场景: 创建订单-数量为0
      假如 存在"产品" 作为 @产品
      当 POST "/orders":
      """
      {
        "product_id": ${{产品.id}},
        "user_id": 1,
        "quantity": 0
      }
      """
      那么 响应状态码应该为 200

      @negative
      场景: 获取不存在的订单
      当 GET "/orders/99999"
      那么 响应字段 "code" 应该为 "404"

      @negative
      场景: 更新不存在的订单
      当 PUT "/orders/99999":
      """
      {
        "product_id": 1,
        "user_id": 1,
        "quantity": 2,
        "status": "paid"
      }
      """
      那么 响应字段 "code" 应该为 "404"

      @negative
      场景: 删除不存在的订单
      当 DELETE "/orders/99999"
      那么 响应字段 "code" 应该为 "404"

      @negative
      场景: 创建订单-库存不足
      假如 存在"产品" 作为 @产品:
        """
        {
          "name": "库存不足产品",
          "price": 100,
          "stock": 1
        }
        """
      当 POST "/orders":
        """
        {
          "product_id": ${{产品.id}},
          "user_id": 1,
          "quantity": 100
        }
        """
      那么 响应字段 "code" 应该为 "400"

      @positive
      场景: 订单金额计算准确性
      假如 存在"产品" 作为 @产品:
        """
        {
          "name": "测试产品",
          "price": 99.99,
          "stock": 100
        }
        """
      当 POST "/orders":
        """
        {
          "product_id": ${{产品.id}},
          "user_id": 1,
          "quantity": 3
        }
        """
      那么 响应状态码应该为 200
      而且 响应数据 "total_amount" 应该为 "299.97"
