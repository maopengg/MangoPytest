# -*- coding: utf-8 -*-
"""
数据清理钩子 - 使用 Repository 模式

通过 repos 目录提供的 Repository 类清理数据，保持一致性
"""
import traceback
import os
import threading
from contextlib import contextmanager
from typing import List, Set, Optional
from dataclasses import dataclass, field

from core.utils import log


@dataclass
class CreatedDataTracker:
    """
    数据创建追踪器 - 记录当前测试/进程创建的数据ID
    
    用于精确清理，只删除当前测试创建的数据
    """
    # 按表名记录创建的ID
    created_ids: dict = field(default_factory=dict)
    # 线程锁
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def add(self, table_name: str, record_id: int):
        """记录创建的数据ID"""
        with self._lock:
            if table_name not in self.created_ids:
                self.created_ids[table_name] = set()
            self.created_ids[table_name].add(record_id)
    
    def add_batch(self, table_name: str, record_ids: List[int]):
        """批量记录创建的数据ID"""
        with self._lock:
            if table_name not in self.created_ids:
                self.created_ids[table_name] = set()
            self.created_ids[table_name].update(record_ids)
    
    def get_ids(self, table_name: str) -> Set[int]:
        """获取指定表记录的ID集合"""
        with self._lock:
            return self.created_ids.get(table_name, set()).copy()
    
    def clear(self):
        """清空记录"""
        with self._lock:
            self.created_ids.clear()
    
    def is_empty(self) -> bool:
        """检查是否有记录"""
        with self._lock:
            return not any(self.created_ids.values())


class TestDataCleaner:
    """
    测试数据清理器 - 使用 Repository 模式
    
    通过 repos 目录提供的 Repository 类清理数据
    """

    def __init__(self, db_session=None):
        self.db_session = db_session
        # 进程ID，用于进程隔离
        self.process_id = os.getpid()
        # 数据追踪器
        self.tracker = CreatedDataTracker()

    def clear_all(self) -> None:
        """
        全局清理 - 清理所有 AUTO_ 开头的测试数据
        
        使用 Repository 模式，通过 delete_auto_test_data() 方法清理
        """
        log.info(">>> [Cleaner] 开始全局清理 AUTO_ 测试数据...")
        
        try:
            # 导入所有 Repository
            from auto_tests.bdd_api_mock.repos import (
                UserRepo,
                ProductRepo,
                OrderRepo,
                DataSubmissionRepo,
                FileRepo,
                ReimbursementRepo,
                DeptApprovalRepo,
                FinanceApprovalRepo,
                CEOApprovalRepo,
                APILogRepo,
            )
            
            # 按依赖顺序清理（先子表后父表）
            # 注意：有外键依赖的表需要先清理
            repos_to_clean = [
                # 1. 审批相关（子表）
                ("部门审批", DeptApprovalRepo),
                ("财务审批", FinanceApprovalRepo),
                ("总经理审批", CEOApprovalRepo),
                # 2. 业务表 - 先清理有外键依赖的子表
                ("报销", ReimbursementRepo),
                ("订单", OrderRepo),
                ("数据", DataSubmissionRepo),
                ("文件", FileRepo),
                # 3. 系统表
                ("API日志", APILogRepo),
                # 4. 业务表 - 后清理父表
                ("产品", ProductRepo),
                # 5. 用户表（最后清理，保留 testuser）
                ("用户", UserRepo),
            ]
            
            total = 0
            for name, repo_class in repos_to_clean:
                try:
                    repo = repo_class(self.db_session)
                    # 检查是否有 delete_auto_test_data 方法
                    if hasattr(repo, 'delete_auto_test_data'):
                        count = repo.delete_auto_test_data()
                        if count > 0:
                            log.info(f"    - {name}: {count} 条")
                        total += count
                    else:
                        log.debug(f"    - {name}: 跳过（无清理方法）")
                except Exception as e:
                    log.warning(f"    - {name}: 清理失败 - {e}")
            
            self.db_session.commit()
            log.info(f">>> [Cleaner] 全局清理完成，共删除 {total} 条记录")
            
        except Exception as e:
            self.db_session.rollback()
            log.error(f">>> [Cleaner] 全局清理失败: {e}")
            traceback.print_exc()

    def clear_by_tracker(self) -> None:
        """
        精确清理 - 只清理 tracker 中记录的数据
        
        适用于：测试用例执行后，只删除自己创建的数据
        """
        if self.tracker.is_empty():
            log.debug(">>> [Cleaner] Tracker 为空，跳过清理")
            return
        
        log.info(">>> [Cleaner] 开始精确清理当前测试数据...")
        
        try:
            from auto_tests.bdd_api_mock.repos import (
                UserRepo,
                ProductRepo,
                OrderRepo,
                DataSubmissionRepo,
                FileRepo,
                ReimbursementRepo,
                DeptApprovalRepo,
                FinanceApprovalRepo,
                CEOApprovalRepo,
            )
            
            # Repo 映射
            repo_map = {
                "users": UserRepo,
                "products": ProductRepo,
                "orders": OrderRepo,
                "data_submissions": DataSubmissionRepo,
                "files": FileRepo,
                "reimbursements": ReimbursementRepo,
                "dept_approvals": DeptApprovalRepo,
                "finance_approvals": FinanceApprovalRepo,
                "ceo_approvals": CEOApprovalRepo,
            }
            
            total = 0
            # 按顺序清理
            cleanup_order = [
                "dept_approvals",
                "finance_approvals",
                "ceo_approvals",
                "reimbursements",
                "orders",
                "data_submissions",
                "files",
                "products",
                "users",
            ]
            
            for table_name in cleanup_order:
                ids = self.tracker.get_ids(table_name)
                if ids and table_name in repo_map:
                    repo_class = repo_map[table_name]
                    repo = repo_class(self.db_session)
                    count = 0
                    for record_id in ids:
                        if repo.delete(record_id):
                            count += 1
                    if count > 0:
                        log.info(f"    - {table_name}: {count} 条")
                    total += count
            
            self.db_session.commit()
            log.info(f">>> [Cleaner] 精确清理完成，共删除 {total} 条记录")
            
        except Exception as e:
            self.db_session.rollback()
            log.error(f">>> [Cleaner] 精确清理失败: {e}")
            traceback.print_exc()
        finally:
            # 清理完成后清空 tracker
            self.tracker.clear()

    def record_created(self, table_name: str, record_id: int):
        """记录创建的数据"""
        self.tracker.add(table_name, record_id)

    def record_created_batch(self, table_name: str, record_ids: List[int]):
        """批量记录创建的数据"""
        self.tracker.add_batch(table_name, record_ids)


@contextmanager
def cleanup_session(db_session_factory):
    """
    数据清理上下文管理器
    
    使用示例：
        with cleanup_session(get_config().SessionLocal) as cleaner:
            # 执行测试...
            cleaner.record_created("users", user_id)
        # 退出上下文时自动清理
    """
    session = db_session_factory()
    cleaner = TestDataCleaner(session)
    try:
        yield cleaner
        # 上下文退出时执行精确清理
        cleaner.clear_by_tracker()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
