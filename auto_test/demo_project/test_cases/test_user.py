# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户管理测试用例 - /users
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure

from auto_test.demo_project.data_factory.builders.auth import AuthBuilder
from auto_test.demo_project.data_factory.builders.user import UserBuilder
from auto_test.demo_project.fixtures.conftest import *


@allure.feature("用户管理")
@allure.story("获取用户")
class TestGetUsers:
    """获取用户接口测试"""

    @allure.title("获取所有用户")
    def test_get_all_users(self, test_token):
        """测试获取所有用户列表"""
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        
        assert isinstance(users, list)
        assert len(users) >= 2  # 默认有2个用户

    @allure.title("根据ID获取用户")
    def test_get_user_by_id(self, test_token):
        """测试根据ID获取用户"""
        user_builder = UserBuilder(token=test_token)
        
        # 先获取所有用户
        users = user_builder.get_all()
        assert len(users) > 0
        
        # 获取第一个用户
        user_id = users[0].get('id')
        user = user_builder.get_by_id(user_id)
        
        assert user is not None
        assert user.get('id') == user_id

    @allure.title("获取不存在的用户")
    def test_get_nonexistent_user(self, test_token):
        """测试获取不存在的用户"""
        user_builder = UserBuilder(token=test_token)
        user = user_builder.get_by_id(99999)
        
        assert user is None


@allure.feature("用户管理")
@allure.story("更新用户")
class TestUpdateUser:
    """更新用户接口测试"""

    @allure.title("正常更新用户信息")
    def test_update_user_success(self, test_token):
        """测试正常更新用户信息"""
        # 先创建一个新用户
        auth_builder = AuthBuilder(token=test_token)
        user = auth_builder.register()
        assert user is not None
        
        user_builder = UserBuilder(token=test_token)
        
        # 更新用户信息
        update_data = {
            "id": user.get('id'),
            "username": user.get('username'),
            "email": "updated@example.com",
            "full_name": "Updated Name",
            "password": user.get('password')
        }
        updated_user = user_builder.update(user.get('id'), update_data)
        
        assert updated_user is not None
        assert updated_user.get('email') == "updated@example.com"
        assert updated_user.get('full_name') == "Updated Name"
        
        # 清理
        user_builder.delete(user.get('id'))

    @allure.title("更新不存在的用户")
    def test_update_nonexistent_user(self, test_token):
        """测试更新不存在的用户"""
        user_builder = UserBuilder(token=test_token)
        
        update_data = {
            "id": 99999,
            "username": "test",
            "email": "test@example.com",
            "full_name": "Test",
            "password": "pass"
        }
        result = user_builder.update(99999, update_data)
        
        assert result is None


@allure.feature("用户管理")
@allure.story("删除用户")
class TestDeleteUser:
    """删除用户接口测试"""

    @allure.title("正常删除用户")
    def test_delete_user_success(self, test_token):
        """测试正常删除用户"""
        # 先创建一个新用户
        auth_builder = AuthBuilder(token=test_token)
        user = auth_builder.register()
        assert user is not None
        user_id = user.get('id')
        
        # 删除用户
        user_builder = UserBuilder(token=test_token)
        result = user_builder.delete(user_id)
        
        assert result is True
        
        # 验证用户已被删除
        deleted_user = user_builder.get_by_id(user_id)
        assert deleted_user is None

    @allure.title("删除不存在的用户")
    def test_delete_nonexistent_user(self, test_token):
        """测试删除不存在的用户"""
        user_builder = UserBuilder(token=test_token)
        result = user_builder.delete(99999)
        
        assert result is False
