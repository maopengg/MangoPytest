# -*- coding: utf-8 -*-
# 用户管理模块 - BDD Feature 文件

Feature: 用户管理
  作为系统管理员
  我希望能够管理用户
  以便维护系统用户数据

  Background:
    Given 管理员已登录系统

  # ==================== 获取用户测试 ====================
  @smoke @positive
  Scenario: 获取所有用户列表
    When 管理员请求获取所有用户
    Then 应该成功返回用户列表
    And 用户列表中至少包含默认用户

  @smoke @positive
  Scenario: 根据ID获取指定用户
    Given 系统中存在测试用户
    When 管理员根据该用户ID查询用户信息
    Then 应该成功返回该用户信息
    And 返回的用户ID应该匹配
    And 返回的用户名应该匹配

  @positive
  Scenario: 获取不同角色的用户
    Given 系统中存在以下角色的用户:
      | role           |
      | admin          |
      | dept_manager   |
      | finance_manager|
      | ceo            |
    When 管理员分别获取这些用户的信息
    Then 所有用户都应该成功返回
    And 每个用户的角色信息应该正确

  @negative
  Scenario: 获取不存在的用户
    When 管理员尝试获取ID为99999的用户
    Then 应该返回用户不存在的信息

  # ==================== 创建用户测试 ====================
  @smoke @positive
  Scenario: 创建新用户
    When 管理员创建一个随机用户
    Then 用户应该创建成功
    And 返回的用户信息应该包含正确的用户名和邮箱

  @positive
  Scenario: 创建多个随机用户
    When 管理员创建 3 个随机用户
    Then 所有用户都应该创建成功

  @positive
  Scenario Outline: 创建不同用户名的用户
    When 管理员创建用户，用户名为 "<username>"
    Then 用户应该创建成功
    And 返回的用户名应该是 "<username>"

    Examples:
      | username      |
      | testuser_001  |
      | user_abc123   |
      | demo_user     |

  @negative
  Scenario: 创建重复用户名的用户
    Given 系统中存在测试用户
    When 管理员尝试创建相同用户名的用户
    Then 用户创建应该失败
    And 系统应该返回错误码 400

  # ==================== 更新用户测试 ====================
  @smoke @positive
  Scenario: 更新用户信息
    Given 系统中存在测试用户
    When 管理员更新该用户的邮箱为 "updated@example.com"
    Then 用户信息应该更新成功
    And 返回的用户邮箱应该是 "updated@example.com"

  @positive
  Scenario: 更新用户全名
    Given 系统中存在测试用户
    When 管理员更新该用户的全名为 "Updated Full Name"
    Then 用户信息应该更新成功
    And 返回的用户全名应该是 "Updated Full Name"

  @negative
  Scenario: 更新不存在的用户
    When 管理员尝试更新ID为99999的用户
    Then 用户更新应该失败
    And 系统应该返回错误码 404

  # ==================== 删除用户测试 ====================
  @smoke @positive
  Scenario: 删除用户
    Given 系统中存在测试用户
    When 管理员删除该用户
    Then 用户应该删除成功
    And 再次获取该用户应该返回不存在

  @positive
  Scenario: 删除多个用户
    Given 管理员创建了三个随机用户
    When 管理员删除这些用户
    Then 所有用户都应该删除成功

  @negative
  Scenario: 删除不存在的用户
    When 管理员尝试删除ID为99999的用户
    Then 用户删除应该失败
    And 系统应该返回错误码 404

  # ==================== 用户角色管理测试 ====================
  @positive
  Scenario: 验证用户角色字段存在
    Given 系统中存在测试用户
    When 管理员获取该用户信息
    Then 返回的用户信息应该包含角色字段

  @positive
  Scenario: 验证默认用户角色
    When 管理员创建一个随机用户
    Then 返回的用户角色应该是 "user"

  # ==================== 集成测试 ====================
  @integration @positive
  Scenario: 完整用户管理流程
    When 管理员创建一个随机用户
    Then 用户应该创建成功
    When 管理员更新该用户的邮箱为 "flow@example.com"
    Then 用户信息应该更新成功
    When 管理员获取该用户信息
    Then 返回的用户邮箱应该是 "flow@example.com"
    When 管理员删除该用户
    Then 用户应该删除成功
