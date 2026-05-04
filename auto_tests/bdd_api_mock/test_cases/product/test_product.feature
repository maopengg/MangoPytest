# language: zh-CN
# -*- coding: utf-8 -*-
功能: 产品管理
  作为系统管理员
  我希望能够管理产品
  以便维护产品数据

  背景:
    假如 管理员已登录

  @smoke @positive
  场景: 获取所有产品列表
    当 GET "/products"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表

  @smoke @positive
  场景: 创建新产品
    当 POST "/products":
      """
      {"name": "新产品", "price": 999.99, "description": "这是一个新产品", "stock": 100}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "id"

  @positive
  场景: 根据ID获取指定产品
    假如 存在"产品"
    当 使用产品ID GET "/products?id=${{product.id}}"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "name"

  @positive
  场景: 更新产品信息
    假如 存在"产品"
    当 使用产品ID PUT "/products/${{product.id}}":
      """
      {"name": "更新后的产品", "price": 888.88, "stock": 50}
      """
    那么 响应状态码应该为 200
    而且 响应数据 "name" 应该为 "更新后的产品"

  @positive
  场景: 删除产品
    假如 存在"产品"
    当 使用产品ID DELETE "/products/${{product.id}}"
    那么 响应状态码应该为 200
