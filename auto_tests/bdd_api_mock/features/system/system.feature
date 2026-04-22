# language: zh-CN
# -*- coding: utf-8 -*-
功能: 系统管理
  作为系统管理员
  我希望能够查看系统状态
  以便监控系统运行情况

  @smoke @positive
  场景: 获取系统健康状态
    当 GET "/system/health"
    那么 响应状态码应该为 200
    而且 响应数据 "status" 应该为 "healthy"

  @smoke @positive
  场景: 获取API日志列表
    假如 管理员已登录
    当 GET "/system/logs"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表
