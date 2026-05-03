# Repos — Repository 数据访问设计

## 职责

封装数据库操作，提供级联清理。UI 测试与 API 测试共用同一套 Repository 逻辑。

## 设计思路

```
UI 测试结束
  → pytest_sessionstart 清理
  → UserRepo.delete_by_pattern("AUTO_%")
  → session.delete(user) → cascade 删关联数据
```

## 写法

```python
class UserRepo(BaseRepository[UserEntity]):
    model = UserEntity
    CODE_FIELD = "username"
```

## 必须遵守

Repository 设计规范与 BDD API 完全相同，详见 [BDD API - Repos](../bdd_api/repos.md)：

- 用 `session.delete()` 而不是裸 SQL `DELETE FROM`
- 每个 Repo 设置 `CODE_FIELD` 指定匹配 `AUTO_%` 的列
- 清理时级联由 Entity 上的 `cascade` 配置自动完成
- 禁止用 `FK_CLEANUP_CONFIG` 或手动排清理顺序

## 与 API 项目的关系

在真实项目中，UI 项目直接导入 API 项目的 Repo：

```python
from auto_tests.<api_project>.repos import UserRepo, ProductRepo
```

避免维护两份副本。
