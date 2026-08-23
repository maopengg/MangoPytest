# Repos — Repository 数据访问设计

## 职责

封装数据库操作，提供统一的 CRUD 接口和测试数据清理。

## 目录结构

```
repos/
├── base.py              # BaseRepository 基类
├── user/
│   └── user_repo.py
├── product/
│   └── product_repo.py
└── ...
```

每个业务模块一个 Repo 子类。

---

## 必须遵守：清理走 ORM 级联，不走裸 SQL

`delete_by_pattern` 用 `session.delete()` 逐条删，触发 Entity 上配置的 cascade。**禁止用 `DELETE FROM table WHERE ...` 裸 SQL 做清理**——裸 SQL 不触发 ORM 级联。

```python
# repos/base.py — 标准实现
class BaseRepository(Generic[T]):
    model: Type[T] = None
    CODE_FIELD: str = None      # 匹配 AUTO_% 的列名

    def delete_by_pattern(self, pattern="AUTO_%") -> int:
        if not self.CODE_FIELD:
            return 0
        # 1. 查出匹配的实体
        stmt = select(self.model).where(
            getattr(self.model, self.CODE_FIELD).like(pattern)
        )
        entities = list(self.session.execute(stmt).scalars().all())
        # 2. 逐个 session.delete() — 触发 ORM cascade
        for entity in entities:
            self.session.delete(entity)
        # 3. 统一提交 — SQLA 自动排好 DELETE 顺序
        self.session.commit()
        return len(entities)
```

对比：

| | `session.delete()` | `DELETE FROM table` |
|---|---|---|
| 触发 ORM cascade | ✅ | ❌ |
| 自动排 FK 顺序 | ✅ | ❌ |
| 子表数据 | 自动删 | 残留 |

---

## 写法

### 子类

```python
class UserRepo(BaseRepository[UserEntity]):
    model = UserEntity
    CODE_FIELD = "username"   # 匹配 AUTO_% 的列

    def get_by_username(self, username):
        stmt = select(UserEntity).where(UserEntity.username == username)
        return self.session.execute(stmt).scalar_one_or_none()
```

### CODE_FIELD 设计

`CODE_FIELD` 指定用哪一列匹配 `AUTO_%` 前缀来做清理：

| 场景 | CODE_FIELD | 说明 |
|------|-----------|------|
| 有命名列 | `"username"`、`"name"`、`"order_no"` | 直接用 |
| 无命名需求 | `None` | 该表不独立清理，数据随父表级联删除 |

---

## 清理流程

清理层只看 Repo，不看 Entity：

```
TestDataCleaner.clear_all()
  → UserRepo.delete_by_pattern("AUTO_%")        # 删 AUTO_ 用户
    → session.delete(user) → cascade 删 orders + reimbursements + ... (ORM 自动)
  → ProductRepo.delete_by_pattern("AUTO_%")     # 删 AUTO_ 产品
    → session.delete(product) → cascade 删 orders (ORM 自动)
  → OrderRepo.delete_by_pattern("AUTO_%")       # 删残留订单（没有 AUTO_ 用户的）
```

### 清理钩子集成

```python
# hooks/cleanup_hooks.py
class TestDataCleaner:
    def clear_all(self):
        repos = [
            DeptApprovalRepo, FinanceApprovalRepo, CEOApprovalRepo,
            ReimbursementRepo, OrderRepo,
            UserRepo, ProductRepo,
        ]
        for repo_class in repos:
            repo = repo_class(self.db_session)
            repo.delete_auto_test_data()
```

### 并行安全

`conftest.py` 中 `pytest_sessionstart` 用文件锁确保 `-n 3` 并行时只有一个 worker 执行清理：

```python
def pytest_sessionstart(session):
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()
```

---

## 新增 Repo

1. 创建 Repo 类，设置 `model` + `CODE_FIELD`
2. 在 `cleanup_hooks.py` 的 `clear_all()` 列表中添加该 Repo
3. 如果有子表依赖，子表 Repo 排在父表 Repo 前面
