# -*- coding: utf-8 -*-
# 产品管理模块 - BDD Feature 文件

Feature: 产品管理
  作为产品管理员
  我希望能够管理产品信息
  以便维护产品目录

  Background:
    Given 管理员已登录系统

  @smoke @positive
  Scenario: 获取所有产品列表
    When 管理员请求获取所有产品
    Then 应该成功返回产品列表
    And 产品列表应该是数组类型
