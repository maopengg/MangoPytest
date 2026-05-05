# language: zh-CN
功能: 统一API响应断言 — 响应应该为:

  场景: 基础状态码和业务字段验证
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "msg": "", "data": {"name": "张三", "age": 25}}
      """
    那么 响应应该为:
      """
      status_code = 200
      body.code = 200
      body.success = true
      """

  场景: 宽松对象匹配 — 只验证关心的字段
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "msg": "", "data": {"id": 1, "name": "张三", "age": 25, "email": "test@test.com"}}
      """
    那么 响应应该为:
      """
      : { status_code: 200, body.code: 200, body.success: true, body.data.name: 张三 }
      """

  场景: 列表数据验证 — 长度和索引访问
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "data": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]}
      """
    那么 响应应该为:
      """
      status_code = 200
      body.data.size = 2
      body.data[0].name = 张三
      body.data[1].id = 2
      """

  场景: 正则匹配
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "data": {"orderId": "ORD-2024-001"}}
      """
    那么 响应应该为:
      """
      body.data.orderId = /ORD-\d{4}-\d{3}/
      """

  场景: 响应体应该为 — 只验证body不验证status_code
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "data": [1, 2, 3]}
      """
    那么 响应体应该为:
      """
      code = 200
      success = true
      data.size = 3
      """

  场景: 空列表
    假如 模拟API响应状态码200
    假如 模拟响应体:
      """
      {"code": 200, "success": true, "data": []}
      """
    那么 响应应该为:
      """
      status_code = 200
      body.data.size = 0
      """
