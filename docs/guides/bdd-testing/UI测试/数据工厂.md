# Data Factory — 数据工厂设计

## 职责

UI 测试与 API 测试共用同一套数据工厂逻辑。在 UI 测试中，数据工厂用于创建测试前置数据（如先创建用户再登录操作页面）。

## 设计思路

```
UI 测试前置条件: 假如 存在"用户"
  → ENTITY_FACTORY_MAP["用户"] → UserSpec
  → factory_boy → INSERT INTO users
  → 页面用该用户登录
```

## 目录结构

```
data_factory/
├── entities/           # SQLAlchemy ORM 模型（与 API 项目相同）
│   ├── user/
│   │   └── user_entity.py
│   └── ...
├── specs/              # factory_boy 工厂
│   ├── user/
│   │   └── user_spec.py
│   └── __init__.py     # ENTITY_FACTORY_MAP 映射表
```

## 写法

### Entity

```python
class UserEntity(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)

    # 必须：声明关联 + 级联删除
    orders = relationship(
        "OrderEntity",
        back_populates="user",
        primaryjoin="UserEntity.id == foreign(OrderEntity.user_id)",
        cascade="all, delete-orphan",
    )
```

### Spec

```python
@register
class UserSpec(BaseFactory):
    class Meta:
        model = UserEntity

    username = factory.LazyFunction(lambda: f"AUTO_USER_{uuid4().hex[:8]}")
    role = "user"
```

## 必须遵守

Entity 设计规范与 BDD API 完全相同，详见 [BDD API - Data Factory](../bdd_api/data_factory.md)：

- 子表列用普通 Integer，不加 `ForeignKey`
- 父表侧必须配 `cascade="all, delete-orphan"` + `primaryjoin`
- 子表侧必须配 `primaryjoin`，对应 `back_populates`
- 禁止 `passive_deletes=True`

## 与 API 项目的关系

在真实项目中，UI 项目通常直接导入 API 项目的 Entity 和 Spec：

```python
# 不复制，直接引用
from auto_tests.<api_project>.data_factory.entities import UserEntity
from auto_tests.<api_project>.data_factory.specs import UserSpec
```

这样可以避免两份代码不同步。如果 UI 项目是独立运行，则自己维护一份 Entity + Spec。
