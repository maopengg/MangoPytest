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
    当 POST "/data/submit":
      """
      {"name": "测试数据", "value": 100}
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "id"

  @smoke @positive
  场景: 获取数据列表
    当 GET "/data"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表
