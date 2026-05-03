# Hooks — 数据清理钩子设计

## 职责

在测试会话开始前自动清理数据库中的残留测试数据。

## 设计思路

```
pytest_sessionstart
  → 尝试获取清理锁（文件锁，xdist 并行互斥）
  → 获取成功 → 遍历所有 Repo 执行 delete_auto_test_data()
  → 获取失败 → 其他 worker 已在清理，跳过
```

## 目录结构

```
hooks/
└── cleanup_hooks.py    # TestDataCleaner + 清理锁
```

## 写法

### 清理器

```python
class TestDataCleaner:
    def __init__(self, db_session):
        self.db_session = db_session

    def clear_all(self):
        """按顺序调用所有 Repo 的 delete_auto_test_data()"""
        repos = [
            DeptApprovalRepo,
            FinanceApprovalRepo,
            CEOApprovalRepo,
            ReimbursementRepo,
            OrderRepo,
            UserRepo,
            ProductRepo,
        ]
        for repo_class in repos:
            repo = repo_class(self.db_session)
            repo.delete_auto_test_data()
```

### 并行安全

多 worker（`-n 3`）时，用文件锁确保只有一个 worker 执行清理：

```python
def _try_acquire_cleanup_lock():
    pid_file = os.path.join(tempfile.gettempdir(), 'project_cleanup.pid')
    if os.path.exists(pid_file):
        # 5 秒内已有其他 worker 清理过
        with open(pid_file) as f:
            _, timestamp = f.read().split(',')
            if time.time() - float(timestamp) < 5:
                return False
    # 写入自己的 PID
    with open(pid_file, 'w') as f:
        f.write(f"{os.getpid()},{time.time()}")
    return True
```

### 集成到 conftest

```python
def pytest_sessionstart(session):
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()

def pytest_sessionfinish(session, exitstatus):
    # 清理锁文件
    os.remove(pid_file)
```

## 清理时机

| 时机 | 操作 |
|------|------|
| `pytest_sessionstart` | 清理上次运行残留 |
| 每个测试 teardown | 不需要——数据在 sessionstart 时统一清 |
| `pytest_sessionfinish` | 释放锁文件 |

## 新增 Repo 时

1. 创建 Repo 类，设置 `CODE_FIELD`
2. 在 `cleanup_hooks.py` 的 `clear_all()` 列表中添加该 Repo
3. 注意清理顺序：子表 Repo 排在父表 Repo 前面
