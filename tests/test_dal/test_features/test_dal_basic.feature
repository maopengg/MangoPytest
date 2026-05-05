Feature: DAL 基础断言

  Scenario: 严格相等
    Given 数据为:
      """
      1
      """
    When 使用 DAL 表达式验证 "= 1"
    Then 验证应该通过

  Scenario: 宽容匹配
    Given 数据为:
      """
      1
      """
    When 使用 DAL 表达式验证 ": 1.0"
    Then 验证应该通过

  Scenario: 比较操作
    Given 数据为:
      """
      10
      """
    When 使用 DAL 表达式验证 "> 5"
    Then 验证应该通过
    When 使用 DAL 表达式验证 "< 20"
    Then 验证应该通过

  Scenario: 逻辑操作
    Given 数据为:
      """
      5
      """
    When 使用 DAL 表达式验证 "> 3 and < 10"
    Then 验证应该通过

  Scenario: 严格相等类型不匹配应该失败
    Given 数据为:
      """
      1
      """
    When 使用 DAL 表达式验证 "= 1.0"
    Then 验证应该失败
