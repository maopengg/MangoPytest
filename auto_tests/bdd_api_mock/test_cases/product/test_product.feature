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
    假如 存在"产品" 作为 @产品
    当 GET "/products?id=${{产品.id}}"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "name"

  @positive
  场景: 更新产品信息
    假如 存在"产品" 作为 @产品
    当 PUT "/products/${{产品.id}}":
      """
      {"name": "更新后的产品", "price": 888.88, "stock": 50}
      """
    那么 响应状态码应该为 200
    而且 响应数据 "name" 应该为 "更新后的产品"

  @positive
  场景: 删除产品
    假如 存在"产品" 作为 @产品
    当 DELETE "/products/${{产品.id}}"
    那么 响应状态码应该为 200

  @negative @boundary
  场景: 创建产品-名称为空
    当 POST "/products":
      """
      {"name": "", "price": 999.99, "description": "这是一个新产品", "stock": 100}
      """
    那么 响应状态码应该为 200

  @negative @boundary
  场景: 创建产品-价格为负数
    当 POST "/products":
      """
      {"name": "测试产品", "price": -100, "description": "这是一个新产品", "stock": 100}
      """
    那么 响应状态码应该为 200

  @negative @boundary
  场景: 创建产品-库存为负数
    当 POST "/products":
      """
      {"name": "测试产品", "price": 999.99, "description": "这是一个新产品", "stock": -10}
      """
    那么 响应状态码应该为 200

  @negative
  场景: 获取不存在的产品
    当 GET "/products?id=99999"
    那么 响应字段 "code" 应该为 "404"

  @negative
  场景: 删除不存在的产品
    当 DELETE "/products/99999"
    那么 响应字段 "code" 应该为 "404"
