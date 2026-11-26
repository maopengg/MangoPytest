  Feature: DAL 表格断言

  Scenario: 宽松表格验证
    Given 存在表格数据:
      """
      | orderId  | status   |
      | ORD-001  | PAID     |
      | ORD-002  | PENDING  |
      """
    When 使用 DAL 表达式验证:
      """
      : | orderId  | status   |
        | ORD-001  | PAID     |
        | ORD-002  | PENDING  |
      """
    Then 验证应该通过

  Scenario: 严格表格验证
    Given 存在表格数据:
      """
      | orderId  | status   |
      | ORD-001  | PAID     |
      | ORD-002  | PENDING  |
      """
    When 使用 DAL 表达式验证:
      """
      = | orderId  | status   |
        | ORD-001  | PAID     |
        | ORD-002  | PENDING  |
      """
    Then 验证应该通过

  Scenario: 表格排序验证
    Given 存在表格数据:
      """
      | id | name |
      | 3  | C    |
      | 1  | A    |
      | 2  | B    |
      """
    When 使用 DAL 表达式验证:
      """
      | id | name | sort by id asc |
      | 1  | A    |
      | 2  | B    |
      | 3  | C    |
      """
    Then 验证应该通过

  Scenario: 表格跳过行验证
    Given 存在表格数据:
      """
      | id | name |
      | 1  | A    |
      | 2  | B    |
      | 3  | C    |
      | 4  | D    |
      """
    When 使用 DAL 表达式验证:
      """
      | id | name | skip 1 |
      | 2  | B    |
      | 3  | C    |
      | 4  | D    |
      """
    Then 验证应该通过
