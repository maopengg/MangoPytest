# -*- coding: utf-8 -*-
# 认证模块 - BDD Feature 文件

Feature: 用户认证
  作为系统用户
  我希望能够登录系统
  以便访问受保护的资源

  Background:
    Given 系统已初始化

  @smoke @positive
  Scenario: 用户注册后成功登录
    Given 用户已注册新用户
    When 用户使用注册凭据发起登录请求
    Then 登录应该成功
    And 系统应该返回有效的访问令牌
    And 用户ID应该被正确设置

  @smoke @negative
  Scenario: 用户使用错误用户名登录失败
    Given 用户准备了错误的用户名
      | username    | password     |
      | wronguser   | password123  |
    When 用户使用这些凭据发起登录请求
    Then 登录应该失败
    And 系统不应该返回访问令牌

  @smoke @negative
  Scenario: 用户使用错误密码登录失败
    Given 用户准备了错误的密码
      | username   | password        |
      | admin      | wrongpassword   |
    When 用户使用这些凭据发起登录请求
    Then 登录应该失败
    And 系统不应该返回访问令牌

  @negative
  Scenario Outline: 用户使用无效凭据登录失败
    Given 用户准备了登录凭据
      | username   | password   |
      | <username> | <password> |
    When 用户使用这些凭据发起登录请求
    Then 登录应该失败
    And 系统应该返回错误码 <error_code>
    And 错误消息应该包含 "<error_message>"

    Examples:
      | username   | password      | error_code | error_message     |
      |            | password123   | 400        | 不能为空          |
      | admin      |               | 401        | 错误              |
      |            |               | 400        | 不能为空          |

  @integration
  Scenario: 登录后使用令牌访问受保护资源
    Given 用户已成功登录
    When 用户使用该令牌获取用户列表
    Then 应该成功获取用户列表
