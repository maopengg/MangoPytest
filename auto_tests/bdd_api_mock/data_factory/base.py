# -*- coding: utf-8 -*-
"""
BDD API Mock 项目 - Factory 基类

所有本项目的 Spec 都应继承此类
"""

from core.base.base_factory import BaseFactory


class BDDAPIBaseFactory(BaseFactory):
    """BDD API Mock 项目的 Factory 基类"""

    class Meta:
        abstract = True
        settings_module = "auto_tests.bdd_api_mock.config"
