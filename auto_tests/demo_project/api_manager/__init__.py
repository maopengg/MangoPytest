# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API管理模块 - 统一的API出口
# @Time   : 2026-03-31
# @Author : 毛鹏

# 统一的API出口
from auto_tests.demo_project.config import load_settings
from .auth import AuthAPI
from .base import DemoProjectBaseAPI
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

    配置token：
        demo_project.set_token("your_token_here")
    """

    def __init__(self):
        self._host = load_settings().HOST
        DemoProjectBaseAPI.set_host(self._host)
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

    def get_host(self) -> str:
        """获取当前API服务器地址"""
        return self._host

    def set_host(self, host: str):
        """
        设置API服务器地址
        @param host: 服务器地址，如 http://localhost:8003
        """
        self._host = host.rstrip("/")
        DemoProjectBaseAPI.set_host(self._host)

    def sync_host_from_env(self, env: str):
        """
        从环境配置同步host
        @param env: 环境名称 (dev/test/pre/prod)
        """
        from auto_tests.demo_project.config import sync_host_from_env
        host = sync_host_from_env(env)
        self.set_host(host)

    def set_token(self, token: str):
        """
        设置认证token
        @param token: JWT token
        """
        DemoProjectBaseAPI.set_token(token)

    def clear_token(self):
        """清除认证token"""
        DemoProjectBaseAPI.clear_token()

    @property
    def auth(self) -> AuthAPI:
        """认证API"""
        if self._auth is None:
            self._auth = AuthAPI()
        return self._auth

    @property
    def user(self) -> UserAPI:
        """用户API"""
        if self._user is None:
            self._user = UserAPI()
        return self._user

    @property
    def product(self) -> ProductAPI:
        """产品API"""
        if self._product is None:
            self._product = ProductAPI()
        return self._product

    @property
    def order(self) -> OrderAPI:
        """订单API"""
        if self._order is None:
            self._order = OrderAPI()
        return self._order

    @property
    def file(self) -> FileAPI:
        """文件API"""
        if self._file is None:
            self._file = FileAPI()
        return self._file

    @property
    def data(self) -> DataAPI:
        """数据API"""
        if self._data is None:
            self._data = DataAPI()
        return self._data

    @property
    def system(self) -> SystemAPI:
        """系统API"""
        if self._system is None:
            self._system = SystemAPI()
        return self._system

    @property
    def login(self) -> LoginAPI:
        """登录API"""
        if self._login is None:
            self._login = LoginAPI()
        return self._login

    # ========== 审批流API ==========

    @property
    def reimbursement(self) -> ReimbursementAPI:
        """报销申请API (D级)"""
        if self._reimbursement is None:
            self._reimbursement = ReimbursementAPI()
        return self._reimbursement

    @property
    def dept_approval(self) -> DeptApprovalAPI:
        """部门审批API (C级)"""
        if self._dept_approval is None:
            self._dept_approval = DeptApprovalAPI()
        return self._dept_approval

    @property
    def finance_approval(self) -> FinanceApprovalAPI:
        """财务审批API (B级)"""
        if self._finance_approval is None:
            self._finance_approval = FinanceApprovalAPI()
        return self._finance_approval

    @property
    def ceo_approval(self) -> CEOApprovalAPI:
        """总经理审批API (A级)"""
        if self._ceo_approval is None:
            self._ceo_approval = CEOApprovalAPI()
        return self._ceo_approval


# 统一的API出口实例
demo_project = DemoProjectAPI()
