# -*- coding: utf-8 -*-
# 系统管理模块 - BDD Feature 文件

Feature: 系统管理
  作为系统管理员
  我希望能够监控系统状态
  以便确保系统正常运行

  Background:
    Given 管理员已登录系统

  @smoke @positive
  Scenario: 健康检查
    When 用户执行健康检查
    Then 健康检查应该成功

  @smoke @positive
  Scenario: 获取服务器信息
    When 用户获取服务器信息
    Then 应该成功返回服务器信息
