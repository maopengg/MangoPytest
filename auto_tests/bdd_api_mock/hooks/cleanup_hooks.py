# -*- coding: utf-8 -*-
"""
数据清理钩子 - 参考 bdd_api_ucai 架构

每次测试执行前清理 AUTO_ 开头的测试数据，保证测试隔离性
"""

import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


class TestDataCleaner:
    """测试数据清理器

    清理所有以 AUTO_ 开头的测试数据
    """

    def __init__(self, db_session=None):
        self.db_session = db_session

    def clear_all(self) -> None:
        """清理所有 AUTO_ 开头的测试数据"""
        logger.info(">>> 开始清理 AUTO_ 测试数据...")

        try:
            # 按照依赖关系顺序清理（先子表后父表）
            cleanup_order = [
                # 1. 审批相关（子表）
                (
                    "dept_approvals",
                    "DELETE FROM dept_approvals WHERE approver_id IN (SELECT id FROM users WHERE username LIKE 'AUTO_%')",
                ),
                (
                    "finance_approvals",
                    "DELETE FROM finance_approvals WHERE approver_id IN (SELECT id FROM users WHERE username LIKE 'AUTO_%')",
                ),
                (
                    "ceo_approvals",
                    "DELETE FROM ceo_approvals WHERE approver_id IN (SELECT id FROM users WHERE username LIKE 'AUTO_%')",
                ),
                # 2. 业务表
                (
                    "reimbursements",
                    "DELETE FROM reimbursements WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'AUTO_%')",
                ),
                ("orders", "DELETE FROM orders WHERE order_no LIKE 'AUTO_%'"),
                (
                    "data_submissions",
                    "DELETE FROM data_submissions WHERE name LIKE 'AUTO_%'",
                ),
                ("files", "DELETE FROM files WHERE filename LIKE 'AUTO_%'"),
                ("products", "DELETE FROM products WHERE name LIKE 'AUTO_%'"),
                # 3. 系统表
                ("api_logs", "DELETE FROM api_logs WHERE id > 0"),  # 清理所有日志
                # 4. 用户表（最后清理，保留 testuser）
                ("users", "DELETE FROM users WHERE username LIKE 'AUTO_%'"),
            ]

            total = 0
            for table_name, sql in cleanup_order:
                try:
                    result = self.db_session.execute(text(sql))
                    count = result.rowcount
                    if count > 0:
                        logger.info(f"    - {table_name}: {count} 条")
                    total += count
                except Exception as e:
                    logger.warning(f"    - {table_name}: 清理失败 - {e}")

            self.db_session.commit()
            logger.info(f">>> 清理完成，共删除 {total} 条记录")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f">>> 清理过程出错: {e}")
            # 不抛出异常，让测试继续
