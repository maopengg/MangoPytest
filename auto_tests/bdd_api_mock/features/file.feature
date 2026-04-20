# -*- coding: utf-8 -*-
# 文件管理模块 - BDD Feature 文件

Feature: 文件上传管理
  作为用户
  我希望能够上传文件
  以便存储和共享文档

  Background:
    Given 用户已登录系统

  @smoke @positive
  Scenario: 正常上传文件
    When 用户上传文件，文件名为 "test.txt"
    Then 文件应该上传成功
