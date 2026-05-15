# Data Factory — 数据工厂设计

## 职责

管理测试数据的创建和结构定义。两层组成：Entity（ORM 模型）+ Spec（工厂）。

## 目录结构

```
data_factory/
├── entities/           # SQLAlchemy ORM 模型（表结构）
│   ├── user/
│   │   └── user_entity.py
│   ├── product/
│   │   └── product_entity.py
│   └── ...
└── specs/              # factory_boy 工厂（数据生成规则）
    ├── user/
    │   └── user_spec.py
    ├── product/
    │   └── product_spec.py
    └── __init__.py     # ENTITY_FACTORY_MAP 映射表
```

---

## 必须遵守：主外键关联 + 级联删除

**数据库有没有外键约束不重要，Entity 里必须用 `relationship` + `primaryjoin` 声明关联，且父表侧必须配 `cascade="all, delete-orphan"`。**

### 为什么必须

测试数据清理靠 `session.delete()` 触发 ORM 级联。如果 Entity 不声明关联：

- 清理时子表数据残留，下次测试重名冲突
- 数据库有外键约束时直接报错 `IntegrityError`

### 规则

| 规则 | 说明 |
|------|------|
| 子表列不加 `ForeignKey` | 用普通 Integer，数据库层面无约束 |
| 父表侧 `relationship` | **必须**带 `primaryjoin` + `cascade="all, delete-orphan"` |
| 子表侧 `relationship` | **必须**带 `primaryjoin`，对应 `back_populates` |
| `primaryjoin` | 用 `foreign(子表.关联列)` 标注方向 |
| **禁止** `passive_deletes=True` | 会让 SQLAlchemy 不处理级联，等数据库自己做 |

### 标准模板

**父表侧（一对多）：**

```python
class ParentEntity(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True)

    children = relationship(
        "ChildEntity",
        back_populates="parent",
        primaryjoin="ParentEntity.id == foreign(ChildEntity.parent_id)",
        cascade="all, delete-orphan",      # 必须：删父时级联删子
    )
```

**子表侧（多对一）：**

```python
class ChildEntity(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=False)   # 不加 ForeignKey

    parent = relationship(
        "ParentEntity",
        back_populates="children",
        primaryjoin="foreign(ChildEntity.parent_id) == ParentEntity.id",
        # 多对一侧不加 cascade
    )
```

### 级联删除链路

只要每个 Entity 都按模板声明关联，删除顶层实体时整条链路自动清理：

```
session.delete(user)
  → UserEntity.orders          cascade → 删 orders
  → UserEntity.reimbursements  cascade → 删 reimbursements
    → ReimbursementEntity.dept_approvals    cascade → 删 dept_approvals
      → DeptApprovalEntity.finance_approvals cascade → 删 finance_approvals
        → FinanceApprovalEntity.ceo_approvals cascade → 删 ceo_approvals
    → ReimbursementEntity.finance_approvals  cascade → 删 finance_approvals
    → ReimbursementEntity.ceo_approvals      cascade → 删 ceo_approvals
    → ReimbursementEntity.approval_logs      cascade → 删 approval_logs
session.commit()
```

**只需删一个 user，整条审批链全部自动清干净。** 不需要手写清理顺序，不需要 `FK_CLEANUP_CONFIG`。

---

## 写法

### Entity（完整示例）

```python
# entities/user/user_entity.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

class UserEntity(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    role = Column(Enum("user", "admin"), default="user")
    status = Column(Enum("active", "inactive"), default="active")
    created_at = Column(DateTime, default=datetime.now)

    # === 关联声明（必须） ===
    orders = relationship(
        "OrderEntity",
        back_populates="user",
        primaryjoin="UserEntity.id == foreign(OrderEntity.user_id)",
        cascade="all, delete-orphan",
    )
```

### Spec（工厂）

```python
# specs/user/user_spec.py
import factory
from pytest_factoryboy import register

@register
class UserSpec(BaseFactory):
    class Meta:
        model = UserEntity

    username = factory.LazyFunction(lambda: f"AUTO_USER_{uuid4().hex[:8]}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    role = "user"
    status = "active"
```

**关键点**：
- `@register` 自动注册为 pytest fixture
- `LazyFunction` / `LazyAttribute` 每次调用计算，保证唯一值
- 数据字段用 `AUTO_` 前缀，配合清理系统按前缀匹配删除

### 中文名映射

```python
# specs/__init__.py
ENTITY_FACTORY_MAP = {
    "用户": UserSpec,
    "产品": ProductSpec,
    "订单": OrderSpec,
    ...
}
```

---

## 常见错误

| 错误写法 | 后果 | 正确写法 |
|---------|------|---------|
| 两边都写 `foreign()` | 方向冲突，SQLA 报错 | 只有一对多侧用 |
| 加了 `passive_deletes=True` | SQLA 跳过级联，子表残留 | 去掉这行 |
| 子表列用了 `ForeignKey` | 数据库必须有对应约束 | 用普通 `Integer` |
| `cascade` 写在多对一侧 | 删子表不会级联删父表 | `cascade` 写在一对多侧 |
| 忘了写 `primaryjoin` | 无 FK 时 SQLA 推导不出关联 | 必须写 |

## 新增实体

1. 在 `entities/<module>/` 创建 Entity，按模板声明 `relationship`
2. 在 `specs/<module>/` 创建 Spec，`@register` 装饰
3. 在 `conftest.py` 添加 `from ... import xxx_spec`
4. 在 `specs/__init__.py` 的 `ENTITY_FACTORY_MAP` 添加中文名映射
