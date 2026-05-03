# -*- coding: utf-8 -*-
"""数据清理钩子 — UI 测试与 API 测试共用同一套清理逻辑"""
import traceback

from core.utils import log


class TestDataCleaner:
    """测试数据清理器"""

    def __init__(self, db_session):
        self.db_session = db_session

    def clear_all(self):
        """全局清理 AUTO_ 测试数据

        按外键依赖顺序调用各 Repo。新增 Repo 时在这里添加即可。
        """
        log.info(">>> [Cleaner] 开始全局清理 AUTO_ 测试数据...")

        # TODO: 项目添加 Entity 和 Repo 后，在这里导入并清理
        # 示例：
        # from auto_tests.<project>.repos.user_repo import UserRepo
        # repos = [UserRepo, ProductRepo, ...]
        # for repo_class in repos:
        #     repo = repo_class(self.db_session)
        #     repo.delete_auto_test_data()

        log.info(">>> [Cleaner] 全局清理完成，共删除 0 条记录")
