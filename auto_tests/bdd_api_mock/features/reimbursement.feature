# -*- coding: utf-8 -*-
# 报销申请模块 - BDD Feature 文件

Feature: 报销申请管理
  作为员工
  我希望能够提交报销申请
  以便获得费用报销

  Background:
    Given 员工已登录系统

  @smoke @positive
  Scenario: 获取所有报销申请
    When 员工请求获取所有报销申请
    Then 应该成功返回报销申请列表
