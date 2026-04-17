# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据工厂 - 根据mock_api接口生成测试数据
# @Time   : 2026-03-31
# @Author : 毛鹏
import hashlib
import uuid
from typing import Dict, Any, List, Optional

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from core.models.api_model import ApiDataModel, RequestModel


class DataFactory:
    """
    数据工厂 - 用于创建和管理测试数据
    对应mock_api.py中的接口：用户、产品、订单、数据、文件等
    """

    def __init__(self):
        self.created_data: Dict[str, List[Dict]] = {
            'users': [],
            'products': [],
            'orders': [],
            'data': []
        }
        self.token: Optional[str] = None

    def _create_api_data(self, url: str, method: str = "GET", json_data: Dict = None,
                         params: Dict = None, headers: Dict = None) -> ApiDataModel:
        """创建ApiDataModel对象"""
        request_model = RequestModel(
            url=url,
            method=method,
            headers=headers or {},
            json=json_data,
            params=params
        )
        return ApiDataModel(request=request_model)

    def login(self, username: str = "testuser", password: str = "482c811da5d5b4bc6d497ffa98491e38") -> str:
        """
        用户登录，获取token
        @param username: 用户名
        @param password: 密码
        @return: token
        """
        data = self._create_api_data(
            url="/auth/login",
            method="POST",
            json_data={"username": username, "password": password}
        )
        result = bdd_api_mock.auth.api_login(data)
        if result.response and result.response.json().get("code") == 200:
            self.token = result.response.json()["data"]["token"]
            return self.token
        return None

    def create_user(self, username: str = None, email: str = None,
                    full_name: str = None, password: str = None) -> Dict[str, Any]:
        """
        创建用户
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码
        @return: 创建的用户数据
        """
        user_data = {
            "username": username or f"user_{uuid.uuid4().hex[:8]}",
            "email": email or f"{uuid.uuid4().hex[:8]}@example.com",
            "full_name": full_name or f"Test User {uuid.uuid4().hex[:4]}",
            "password": password or hashlib.md5("123456".encode()).hexdigest()
        }

        api_data = self._create_api_data(
            url="/auth/register",
            method="POST",
            json_data=user_data
        )

        result = bdd_api_mock.auth.api_register(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_user = result.response.json()["data"]
            self.created_data['users'].append(created_user)
            return created_user
        return None

    def get_user(self, user_id: int = None) -> Dict[str, Any]:
        """
        获取用户
        @param user_id: 用户ID，不传则获取所有用户
        @return: 用户数据
        """
        params = {"id": user_id} if user_id else None
        api_data = self._create_api_data(
            url="/users",
            method="GET",
            params=params,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.user.get_all_users(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户
        @param user_id: 用户ID
        @param user_data: 用户数据
        @return: 更新后的用户数据
        """
        api_data = self._create_api_data(
            url="/users",
            method="PUT",
            params={"id": user_id},
            json_data=user_data,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.user.update_user_info(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        @param user_id: 用户ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/users",
            method="DELETE",
            params={"id": user_id},
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.user.delete_user(api_data)
        if result.response and result.response.json().get("code") == 200:
            # 从记录中移除
            self.created_data['users'] = [
                u for u in self.created_data['users']
                if u.get('id') != user_id
            ]
            return True
        return False

    def create_product(self, name: str = None, price: float = None,
                       description: str = None) -> Dict[str, Any]:
        """
        创建产品
        @param name: 产品名称
        @param price: 产品价格
        @param description: 产品描述
        @return: 创建的产品数据
        """
        product_data = {
            "name": name or f"Product {uuid.uuid4().hex[:6]}",
            "price": price or 99.99,
            "description": description or f"Description for product {uuid.uuid4().hex[:6]}"
        }

        api_data = self._create_api_data(
            url="/products",
            method="POST",
            json_data=product_data,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.product.create_product(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_product = result.response.json()["data"]
            self.created_data['products'].append(created_product)
            return created_product
        return None

    def get_product(self, product_id: int = None) -> Dict[str, Any]:
        """
        获取产品
        @param product_id: 产品ID，不传则获取所有产品
        @return: 产品数据
        """
        params = {"id": product_id} if product_id else None
        api_data = self._create_api_data(
            url="/products",
            method="GET",
            params=params,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.product.get_all_products(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新产品
        @param product_id: 产品ID
        @param product_data: 产品数据
        @return: 更新后的产品数据
        """
        api_data = self._create_api_data(
            url="/products",
            method="PUT",
            params={"id": product_id},
            json_data=product_data,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.product.update_product_info(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def delete_product(self, product_id: int) -> bool:
        """
        删除产品
        @param product_id: 产品ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/products",
            method="DELETE",
            params={"id": product_id},
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.product.delete_product(api_data)
        if result.response and result.response.json().get("code") == 200:
            self.created_data['products'] = [
                p for p in self.created_data['products']
                if p.get('id') != product_id
            ]
            return True
        return False

    def create_order(self, product_id: int, quantity: int, user_id: int) -> Dict[str, Any]:
        """
        创建订单
        @param product_id: 产品ID
        @param quantity: 数量
        @param user_id: 用户ID
        @return: 创建的订单数据
        """
        order_data = {
            "product_id": product_id,
            "quantity": quantity,
            "user_id": user_id
        }

        api_data = self._create_api_data(
            url="/orders",
            method="POST",
            json_data=order_data,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.order.create_order(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_order = result.response.json()["data"]
            self.created_data['orders'].append(created_order)
            return created_order
        return None

    def get_order(self, order_id: int = None) -> Dict[str, Any]:
        """
        获取订单
        @param order_id: 订单ID，不传则获取所有订单
        @return: 订单数据
        """
        if order_id:
            api_data = self._create_api_data(
                url=f"/orders/{order_id}",
                method="GET",
                headers={"X-Token": self.token}
            )
            result = bdd_api_mock.order.get_order_by_id(api_data)
        else:
            api_data = self._create_api_data(
                url="/orders",
                method="GET",
                headers={"X-Token": self.token}
            )
            result = bdd_api_mock.order.get_all_orders(api_data)

        if result.response:
            return result.response.json().get("data")
        return None

    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新订单
        @param order_id: 订单ID
        @param order_data: 订单数据
        @return: 更新后的订单数据
        """
        api_data = self._create_api_data(
            url="/orders",
            method="PUT",
            params={"id": order_id},
            json_data=order_data,
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.order.update_order_info(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def delete_order(self, order_id: int) -> bool:
        """
        删除订单
        @param order_id: 订单ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/orders",
            method="DELETE",
            params={"id": order_id},
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.order.delete_order(api_data)
        if result.response and result.response.json().get("code") == 200:
            self.created_data['orders'] = [
                o for o in self.created_data['orders']
                if o.get('id') != order_id
            ]
            return True
        return False

    def submit_data(self, name: str, value: int) -> Dict[str, Any]:
        """
        提交数据
        @param name: 数据名称
        @param value: 数据值
        @return: 提交结果
        """
        api_data = self._create_api_data(
            url="/api/data",
            method="POST",
            json_data={"name": name, "value": value},
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.data.submit_data(api_data)
        if result.response:
            data_result = result.response.json()
            if data_result.get("code") == 200:
                self.created_data['data'].append(data_result.get("data"))
            return data_result.get("data")
        return None

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        @return: 健康状态
        """
        api_data = self._create_api_data(
            url="/health",
            method="GET",
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.system.health_check(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息
        @return: 服务器信息
        """
        api_data = self._create_api_data(
            url="/info",
            method="GET",
            headers={"X-Token": self.token}
        )

        result = bdd_api_mock.system.get_server_info(api_data)
        if result.response:
            return result.response.json().get("data")
        return None

    def cleanup_all(self):
        """清理所有创建的数据"""
        # 删除所有订单
        for order in self.created_data['orders'][:]:  # 使用切片复制列表
            self.delete_order(order.get('id'))

        # 删除所有产品
        for product in self.created_data['products'][:]:  # 使用切片复制列表
            self.delete_product(product.get('id'))

        # 删除所有用户
        for user in self.created_data['users'][:]:  # 使用切片复制列表
            self.delete_user(user.get('id'))

        # 清空数据记录
        self.created_data = {
            'users': [],
            'products': [],
            'orders': [],
            'data': []
        }
