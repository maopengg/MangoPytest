# -*- coding: utf-8 -*-
# 数据管理模块 - BDD Feature 文件

Feature: 数据提交管理
  作为系统用户
  我希望能够提交数据
  以便记录指标和统计信息

  Background:
    Given 用户已登录系统

  @smoke @positive
  Scenario: 正常提交数据
    When 用户提交名称为 "test_metric" 的数据，值为 100
    Then 数据应该提交成功
