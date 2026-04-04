# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API管理模块 - 统一的API出口
# @Time   : 2026-03-31
# @Author : 毛鹏

from typing import Optional

# 统一的API出口
from auto_tests.demo_project.config import load_settings
from .auth import AuthAPI
from .ceo_approval import CEOApprovalAPI
from .data import DataAPI
from .dept_approval import DeptApprovalAPI
from .file import FileAPI
from .finance_approval import FinanceApprovalAPI
from .login import LoginAPI
from .order import OrderAPI
from .product import ProductAPI
# 审批流API
from .reimbursement import ReimbursementAPI
from .system import SystemAPI
from .user import UserAPI


class DemoProjectAPI:
    """
    统一的API出口类
    使用方式: demo_project.auth.api_login(data)

    配置host：
        demo_project.set_host("http://localhost:8003")
        demo_project.sync_host_from_env("pre")
    """

    # Mock API 默认地址（兜底值）
    DEFAULT_HOST = "http://localhost:8003"

    def __init__(self):
        self._host = load_settings().HOST or self.DEFAULT_HOST
        self._auth = None
        self._user = None
        self._product = None
        self._order = None
        self._file = None
        self._data = None
        self._system = None
        self._login = None
        # 审批流API
        self._reimbursement = None
        self._dept_approval = None
        self._finance_approval = None
        self._ceo_approval = None

    def sync_host_from_env(self, env: Optional[str] = None) -> str:
        """
        根据配置环境同步 host

        @param env: 指定环境（dev/test/pre/prod），不传则使用当前 ENV
        @return: 生效后的 host
        """
        config = load_settings(env)
        self.set_host(config.HOST or self.DEFAULT_HOST)
        return self._host

    def set_host(self, host: str):
        """
        设置API服务器地址
        @param host: 服务器地址，如 http://localhost:8003
        """
        self._host = host.rstrip("/")
        # 更新所有已创建的API实例的host
        for api in [
            self._auth,
            self._user,
            self._product,
            self._order,
            self._file,
            self._data,
            self._system,
            self._login,
            self._reimbursement,
            self._dept_approval,
            self._finance_approval,
            self._ceo_approval,
        ]:
            if api is not None:
                api.set_host(self._host)

    def get_host(self) -> str:
        """获取当前API服务器地址"""
        return self._host

    @property
    def auth(self) -> AuthAPI:
        """认证API"""
        if self._auth is None:
            self._auth = AuthAPI()
            self._auth.set_host(self._host)
        return self._auth

    @property
    def user(self) -> UserAPI:
        """用户API"""
        if self._user is None:
            self._user = UserAPI()
            self._user.set_host(self._host)
        return self._user

    @property
    def product(self) -> ProductAPI:
        """产品API"""
        if self._product is None:
            self._product = ProductAPI()
            self._product.set_host(self._host)
        return self._product

    @property
    def order(self) -> OrderAPI:
        """订单API"""
        if self._order is None:
            self._order = OrderAPI()
            self._order.set_host(self._host)
        return self._order

    @property
    def file(self) -> FileAPI:
        """文件API"""
        if self._file is None:
            self._file = FileAPI()
            self._file.set_host(self._host)
        return self._file

    @property
    def data(self) -> DataAPI:
        """数据API"""
        if self._data is None:
            self._data = DataAPI()
            self._data.set_host(self._host)
        return self._data

    @property
    def system(self) -> SystemAPI:
        """系统API"""
        if self._system is None:
            self._system = SystemAPI()
            self._system.set_host(self._host)
        return self._system

    @property
    def login(self) -> LoginAPI:
        """登录API"""
        if self._login is None:
            self._login = LoginAPI()
            self._login.set_host(self._host)
        return self._login

    # ========== 审批流API ==========

    @property
    def reimbursement(self) -> ReimbursementAPI:
        """报销申请API (D级)"""
        if self._reimbursement is None:
            self._reimbursement = ReimbursementAPI()
            self._reimbursement.set_host(self._host)
        return self._reimbursement

    @property
    def dept_approval(self) -> DeptApprovalAPI:
        """部门审批API (C级)"""
        if self._dept_approval is None:
            self._dept_approval = DeptApprovalAPI()
            self._dept_approval.set_host(self._host)
        return self._dept_approval

    @property
    def finance_approval(self) -> FinanceApprovalAPI:
        """财务审批API (B级)"""
        if self._finance_approval is None:
            self._finance_approval = FinanceApprovalAPI()
            self._finance_approval.set_host(self._host)
        return self._finance_approval

    @property
    def ceo_approval(self) -> CEOApprovalAPI:
        """总经理审批API (A级)"""
        if self._ceo_approval is None:
            self._ceo_approval = CEOApprovalAPI()
            self._ceo_approval.set_host(self._host)
        return self._ceo_approval


# 统一的API出口实例
demo_project = DemoProjectAPI()
