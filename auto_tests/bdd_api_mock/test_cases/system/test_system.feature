# language: zh-CN
# -*- coding: utf-8 -*-
功能: 系统管理
  作为系统管理员
  我希望能够查看系统状态
  以便监控系统运行情况

  背景:
    假如 用户"testuser"已登录

  @smoke @positive
  场景: 获取系统健康状态
    当 GET "/health" 预期失败
    那么 响应状态码应该为 403

  @smoke @positive
  场景: 获取服务器信息
    当 GET "/info" 预期失败
    那么 响应状态码应该为 403

  @smoke @positive
  场景: 初始化数据成功
    当 GET "/startup"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "message"

  @negative @security
  场景: 健康检查-未授权访问
    假如 未登录用户
    当 GET "/health" 预期失败
    那么 响应状态码应该为 401

  @negative @security
  场景: 服务器信息-未授权访问
    假如 未登录用户
    当 GET "/info" 预期失败
    那么 响应状态码应该为 401

  @negative @security
  场景: 健康检查-自定义密钥错误
    假如 用户"testuser"已登录
    当 GET "/health?X-Custom-Key=wrong_key&X-Request-Source=test" 预期失败
    那么 响应状态码应该为 403

  @positive
  场景: 访问首页成功
    当 GET "/"
    那么 响应状态码应该为 200

  @positive
  场景: 重复初始化数据
    当 GET "/startup"
    那么 响应状态码应该为 200
    当 GET "/startup"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "message"
