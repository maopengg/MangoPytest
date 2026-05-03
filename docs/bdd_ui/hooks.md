# Hooks — 数据清理钩子设计

## 职责

在测试会话开始前自动清理数据库测试数据。与 BDD API 共用同一套清理逻辑。

## 设计思路

```
pytest_sessionstart
  → 尝试获取清理锁（xdist 并行互斥）
  → 遍历所有 Repo → delete_auto_test_data()
  → session.delete() → ORM cascade 清理整条链路
```

## 写法

```python
class TestDataCleaner:
    def clear_all(self):
        # 添加 Entity 和 Repo 后，在这里导入并清理：
        # from auto_tests.<project>.repos import UserRepo
        # repos = [UserRepo, ProductRepo, ...]
        # for repo_class in repos:
        #     repo = repo_class(self.db_session)
        #     repo.delete_auto_test_data()
        pass
```

## 集成到 conftest

```python
def pytest_sessionstart(session):
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()

def pytest_sessionfinish(session, exitstatus):
    # 释放锁文件
```

## 并行安全

与 BDD API 使用相同的文件锁机制，确保 `-n 3` 并行时只有一个 worker 执行清理。详见 [BDD API - Hooks](../bdd_api/hooks.md)。
