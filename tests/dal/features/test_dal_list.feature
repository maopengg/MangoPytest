Feature: DAL 列表断言
  作为测试人员
  我需要验证列表数据的大小和内容
  以便确保返回的列表数据正确

  Scenario: 列表大小验证
    Given 列表数据为:
      """
      [
        {"id": 1},
        {"id": 2},
        {"id": 3}
      ]
      """
    When 验证列表:
      """
      .size = 3
      """
    Then 验证应该通过

  Scenario: 列表大小不匹配应失败
    Given 列表数据为:
      """
      [
        {"id": 1},
        {"id": 2}
      ]
      """
    When 验证列表:
      """
      .size = 3
      """
    Then 验证应该失败

  Scenario: 列表索引访问
    Given 列表数据为:
      """
      [
        {"id": 1, "name": "张三"},
        {"id": 2, "name": "李四"}
      ]
      """
    When 验证列表:
      """
      [0].id = 1
      """
    Then 验证应该通过

  Scenario: 列表索引访问 - 第二个元素
    Given 列表数据为:
      """
      [
        {"id": 1, "name": "张三"},
        {"id": 2, "name": "李四"}
      ]
      """
    When 验证列表:
      """
      [1].name = '李四'
      """
    Then 验证应该通过

  Scenario: 严格列表匹配
    Given 列表数据为:
      """
      [
        {"orderId": "ORD-001", "status": "PAID"},
        {"orderId": "ORD-002", "status": "PENDING"}
      ]
      """
    When 验证列表:
      """
      = [{
        orderId: 'ORD-001'
        status: PAID
      } {
        orderId: 'ORD-002'
        status: PENDING
      }]
      """
    Then 验证应该通过

  Scenario: 严格列表匹配 - 长度不匹配应失败
    Given 列表数据为:
      """
      [
        {"id": 1}
      ]
      """
    When 验证列表:
      """
      = [{
        id: 1
      } {
        id: 2
      }]
      """
    Then 验证应该失败

  Scenario: 空列表验证
    Given 列表数据为:
      """
      []
      """
    When 验证列表:
      """
      .size = 0
      """
    Then 验证应该通过

  Scenario: 列表元素比较
    Given 列表数据为:
      """
      [10, 20, 30]
      """
    When 验证列表:
      """
      [0] = 10
      """
    Then 验证应该通过

  Scenario: 列表元素范围比较
    Given 列表数据为:
      """
      [10, 20, 30]
      """
    When 验证列表:
      """
      [1] > 15 and [1] < 25
      """
    Then 验证应该通过
