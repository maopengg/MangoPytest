# language: zh-CN
# -*- coding: utf-8 -*-
功能: 数据提交管理
  作为系统用户
  我希望能够提交数据
  以便记录信息

  背景:
    假如 用户"testuser"已登录

  @smoke @positive
  场景: 提交数据
    当 POST "/api/data":
      """
      {
        "name": "测试数据",
        "value": "100"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "name"

  @smoke @negative
  场景: 提交数据缺少参数
    当 POST "/api/data":
      """
      {}
      """
    那么 响应状态码应该为 200
    而且 响应字段 "code" 应该为 "400"

  @negative @boundary
  场景: 提交数据-value为空
    当 POST "/api/data":
      """
      {
        "name": "测试数据",
        "value": ""
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @negative
  场景: 提交数据-value非整数
    当 POST "/api/data":
      """
      {
        "name": "测试数据",
        "value": "abc"
      }
      """
    那么 响应字段 "code" 应该为 "400"

  @positive
  场景: 提交数据成功-query参数
    当 POST "/api/data?name=query测试&value=200":
      """
      {}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "name"

  @positive
  场景: 提交数据-body覆盖query
    当 POST "/api/data?name=query值&value=300":
      """
      {
        "name": "body值",
        "value": "400"
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据 "name" 应该为 "body值"
