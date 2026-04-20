# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
报销申请模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.reimbursement import (
    ReimbursementBuilder,
)
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("员工已创建测试报销申请", target_fixture="test_reimbursement")
def prepare_test_reimbursement(employee_logged_in):
    """准备测试报销申请"""
    token = employee_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=500.00, reason="测试报销"
    )
    return reimbursement


# ==================== When 步骤 ====================


@when("员工创建报销申请，数据如下:", target_fixture="created_reimbursement")
def employee_create_reimbursement(employee_logged_in, table):
    """员工创建报销申请"""
    token = employee_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    rows = list(table)

    reimbursement = reimbursement_builder.create(
        user_id=1, amount=float(rows[0]["amount"]), reason=rows[0]["reason"]
    )
    return reimbursement


@when("员工批量创建以下报销申请:", target_fixture="created_reimbursements")
def employee_create_multiple_reimbursements(employee_logged_in, table):
    """员工批量创建报销申请"""
    token = employee_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    reimbursements = []

    for row in table:
        reimbursement = reimbursement_builder.create(
            user_id=1, amount=float(row["amount"]), reason=row["reason"]
        )
        reimbursements.append(reimbursement)
    return reimbursements


@when("员工请求获取所有报销申请", target_fixture="reimbursements_list")
def employee_get_all_reimbursements(employee_logged_in):
    """员工获取所有报销申请"""
    token = employee_logged_in["token"]
    bdd_api_mock.reimbursement.set_token(token)
    result = bdd_api_mock.reimbursement.get_reimbursements()
    return result


@when("员工根据该报销申请ID查询信息", target_fixture="fetched_reimbursement")
def employee_get_reimbursement_by_id(employee_logged_in, test_reimbursement):
    """员工根据ID获取报销申请"""
    token = employee_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)

    reimbursement_id = (
        test_reimbursement.id
        if hasattr(test_reimbursement, "id")
        else test_reimbursement["id"]
    )
    reimbursement = reimbursement_builder.get_by_id(reimbursement_id)
    return reimbursement


# ==================== Then 步骤 ====================


@then("报销申请应该创建成功")
def verify_reimbursement_created(created_reimbursement):
    """验证报销申请创建成功"""
    assert created_reimbursement is not None


@then("报销申请应该包含有效的ID")
def verify_reimbursement_has_id(created_reimbursement):
    """验证报销申请包含有效ID"""
    reimbursement_id = (
        created_reimbursement.id
        if hasattr(created_reimbursement, "id")
        else created_reimbursement["id"]
    )
    assert reimbursement_id is not None


@then(parsers.parse("报销金额应该是 {amount:f}"))
def verify_reimbursement_amount(created_reimbursement, amount):
    """验证报销金额"""
    reimbursement_amount = (
        created_reimbursement.amount
        if hasattr(created_reimbursement, "amount")
        else created_reimbursement["amount"]
    )
    assert reimbursement_amount == amount


@then(parsers.parse('报销状态应该是 "{status}"'))
def verify_reimbursement_status(created_reimbursement, status):
    """验证报销状态"""
    reimbursement_status = (
        created_reimbursement.status
        if hasattr(created_reimbursement, "status")
        else created_reimbursement["status"]
    )
    assert reimbursement_status == status


@then("报销申请应该创建失败")
def verify_reimbursement_creation_failed(created_reimbursement):
    """验证报销申请创建失败"""
    # 对于无效金额，builder可能返回None或抛出异常
    # 这里假设返回None表示失败
    assert created_reimbursement is None or (
        hasattr(created_reimbursement, "status")
        and created_reimbursement.status == "error"
    )


@then("所有报销申请都应该创建成功")
def verify_all_reimbursements_created(created_reimbursements):
    """验证所有报销申请都创建成功"""
    for reimbursement in created_reimbursements:
        assert reimbursement is not None


@then(parsers.parse("总共应该创建 {count:d} 个报销申请"))
def verify_reimbursements_count(created_reimbursements, count):
    """验证创建的报销申请数量"""
    assert len(created_reimbursements) == count


@then("应该成功返回报销申请列表")
def verify_reimbursements_list_returned(reimbursements_list):
    """验证成功返回报销申请列表"""
    assert reimbursements_list.get("code") == 200
    assert isinstance(reimbursements_list.get("data"), list)


@then("应该成功返回该报销申请信息")
def verify_reimbursement_returned(fetched_reimbursement):
    """验证成功返回报销申请信息"""
    assert fetched_reimbursement is not None


@then("返回的报销申请ID应该匹配")
def verify_reimbursement_id_matches(fetched_reimbursement, test_reimbursement):
    """验证返回的报销申请ID匹配"""
    expected_id = (
        test_reimbursement.id
        if hasattr(test_reimbursement, "id")
        else test_reimbursement["id"]
    )
    actual_id = (
        fetched_reimbursement.id
        if hasattr(fetched_reimbursement, "id")
        else fetched_reimbursement["id"]
    )
    assert actual_id == expected_id
