# -*- coding: utf-8 -*-
# 订单管理模块 - BDD Feature 文件

Feature: 订单管理
  作为用户
  我希望能够创建和管理订单
  以便购买产品

  Background:
    Given 用户已登录系统

  @smoke @positive
  Scenario: 获取所有订单
    When 用户请求获取所有订单
    Then 应该成功返回订单列表
