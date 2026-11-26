Feature: DAL 对象断言

  Scenario: 宽容对象验证
    Given 数据为:
      """
      {
        "name": "张三",
        "age": 25,
        "email": "test@test.com"
      }
      """
    When 使用 DAL 表达式验证:
      """
      : {
        name: '张三'
        age: 25
      }
      """
    Then 验证应该通过

  Scenario: 严格对象验证
    Given 数据为:
      """
      {
        "name": "张三",
        "age": 25
      }
      """
    When 使用 DAL 表达式验证:
      """
      = {
        name: '张三'
        age: 25
      }
      """
    Then 验证应该通过

  Scenario: 嵌套对象验证
    Given 数据为:
      """
      {
        "name": "张三",
        "address": {
          "city": "北京",
          "zip": "100000"
        }
      }
      """
    When 使用 DAL 表达式验证:
      """
      : {
        address.city: '北京'
        address.zip: '100000'
      }
      """
    Then 验证应该通过

  Scenario: 严格对象有多余字段应该失败
    Given 数据为:
      """
      {
        "name": "张三",
        "age": 25,
        "extra": "field"
      }
      """
    When 使用 DAL 表达式验证:
      """
      = {
        name: '张三'
        age: 25
      }
      """
    Then 验证应该失败
