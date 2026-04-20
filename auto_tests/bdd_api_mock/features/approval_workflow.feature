# -*- coding: utf-8 -*-
# 审批流程模块 - BDD Feature 文件
# 展示复杂业务流程的 BDD 测试设计

Feature: 报销审批流程
  作为审批人
  我希望能够审批报销申请
  以便控制费用支出

  Background:
    Given 审批人已登录系统

  # ==================== 基础查询测试 ====================
  @smoke @positive
  Scenario: 获取所有审批记录
    When 审批人请求获取所有审批记录
    Then 应该成功返回审批记录列表

  # ==================== 部门审批测试 ====================
  @integration @positive
  Scenario: 部门经理审批通过报销申请
    Given 员工提交了金额为 5000 元的报销申请
    When 部门经理审批通过
    Then 报销申请状态应该为 "dept_approved"

  @integration @negative
  Scenario: 部门经理审批拒绝报销申请
    Given 员工提交了金额为 3000 元的报销申请
    When 部门经理审批拒绝，理由为 "不符合报销规定"
    Then 报销申请状态应该为 "dept_rejected"

  # ==================== 参数化测试 ====================
  @integration @positive @parameterized
  Scenario Outline: 不同金额级别的报销审批
    Given 员工提交了金额为 <amount> 元的报销申请
    When 部门经理审批通过
    Then 报销申请应该被成功审批

    Examples:
      | amount |
      | 1000   |
      | 5000   |
      | 10000  |
      | 20000  |

  # ==================== 边界值测试 ====================
  @integration @boundary
  Scenario: 最小金额报销审批
    Given 员工提交了金额为 0.01 元的报销申请
    When 部门经理审批通过
    Then 报销申请应该被成功审批

  @integration @boundary
  Scenario: 超大金额报销审批
    Given 员工提交了金额为 999999.99 元的报销申请
    When 部门经理审批通过
    Then 报销申请应该被成功审批

  # ==================== 状态流转测试 ====================
  @integration @state_transition
  Scenario: 报销申请状态流转 - 待审批到已审批
    Given 员工提交了金额为 5000 元的报销申请
    Then 报销申请状态应该为 "pending"
    When 部门经理审批通过
    Then 报销申请状态应该为 "dept_approved"

  @integration @state_transition
  Scenario: 报销申请状态流转 - 待审批到已拒绝
    Given 员工提交了金额为 3000 元的报销申请
    Then 报销申请状态应该为 "pending"
    When 部门经理审批拒绝
    Then 报销申请状态应该为 "dept_rejected"

  # ==================== 并发测试 ====================
  @integration @concurrent
  Scenario: 多个报销申请同时审批
    Given 员工提交了 5 个报销申请
    When 所有申请都经过部门审批
    Then 所有申请的状态都应该为 "dept_approved"

  # ==================== 特殊场景测试 ====================
  @integration @special
  Scenario: 修改待审批的报销申请
    Given 员工提交了金额为 5000 元的报销申请
    When 员工修改报销金额为 6000 元
    Then 修改应该成功
    And 报销申请状态应该仍为 "pending"
