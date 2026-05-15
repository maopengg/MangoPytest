# Core 目录重构详细方案

> 版本：v1.0
> 日期：2026-05-03
> 目标：简化 core/ 目录结构，消除模块冗余和职责重叠

---

## 一、重构目标

### 1.1 当前问题
- **模块过多**：core/ 下有 12 个子目录，部分目录文件过多
- **职责重叠**：`BuilderContext`、`StrategyResult` 等类重复定义
- **未使用代码**：`data_factory_base.py` 等文件未被引用
- **过度设计**：DAL 层实现了完整的解析器，可能未使用

### 1.2 重构原则
1. **删除未使用代码** - 减少维护负担
2. **合并重复概念** - 统一类定义
3. **按职责分组** - 清晰的模块边界
4. **保持向后兼容** - 通过 `__init__.py` 导出保持 API 不变

---

## 二、重构前后对比

### 2.1 当前结构（12个目录，50+文件）

```
core/
├── api/              # 4 files
├── base/             # 11 files ⚠️
├── dal/              # 10 files ⚠️
├── decorators/       # 2 files
├── enums/            # 4 files
├── exceptions/       # 2 files
├── models/           # 7 files
├── reporting/        # 8 files ⚠️
├── settings/         # 2 files
├── sources/          # 2 files
├── ui/               # 2 files
└── utils/            # 6 files
```

### 2.2 目标结构（8个目录，30+文件）

```
core/
├── api/              # 4 files (保持不变)
├── data/             # 7 files (合并 base/ + dal/)
├── models/           # 6 files (已优化)
├── testing/          # 3 files (新增，合并 layering + reporting)
├── ui/               # 1 file  (简化)
├── config/           # 1 file  (重命名 settings/)
├── enums/            # 4 files (保持不变)
├── exceptions/       # 2 files (保持不变)
├── sources/          # 2 files (保持不变)
└── utils/            # 6 files (保持不变)
```

---

## 三、详细重构步骤

### 阶段一：删除未使用文件（高优先级）

#### 步骤 1.1：验证并删除 data_factory_base.py

**验证命令：**
```bash
grep -r "DataFactoryBase" --include="*.py" d:\code\MangoPytest\
grep -r "from.*data_factory_base" --include="*.py" d:\code\MangoPytest\
```

**操作：**
- [ ] 如果无引用，删除 `core/base/data_factory_base.py`

#### 步骤 1.2：验证并删除 builder_context.py 和 strategy_result.py

**验证命令：**
```bash
grep -r "from.*builder_context" --include="*.py" d:\code\MangoPytest\
grep -r "from.*strategy_result" --include="*.py" d:\code\MangoPytest\
```

**操作：**
- [ ] 如果仅被 `base/` 内部引用，删除：
  - `core/base/builder_context.py`
  - `core/base/strategy_result.py`
- [ ] 更新引用到 `core/models/strategy.py`

#### 步骤 1.3：验证 DAL 使用情况

**验证命令：**
```bash
grep -r "from core.dal" --include="*.py" d:\code\MangoPytest\auto_tests\
grep -r "expect\(" --include="*.py" d:\code\MangoPytest\auto_tests\
grep -r "\.should\(" --include="*.py" d:\code\MangoPytest\auto_tests\
```

**决策：**
- [ ] 如果 DAL 未被使用，删除整个 `core/dal/` 目录
- [ ] 如果被使用，保留简化版本

---

### 阶段二：合并 base/ 和 dal/ 为 data/（中优先级）

#### 步骤 2.1：创建新的 data/ 目录

**新文件结构：**
```
core/data/
├── __init__.py
├── factory.py          # 原 baseFactory.py
├── builder.py          # base_builder.py + BuilderContext
├── entity.py           # base_entity.py + pydantic_base.py
├── strategy.py         # base_strategy.py + StrategyResult
├── repository.py       # repository_base.py
├── config.py           # config.py
└── assert_lang.py      # 简化版 DAL（可选）
```

#### 步骤 2.2：创建 core/data/__init__.py

```python
# -*- coding: utf-8 -*-
"""
数据层模块 - 提供数据创建、管理和访问的基础功能

包含：
- Factory: 数据工厂模式
- Builder: 构建器模式
- Entity: 实体基类
- Strategy: 策略模式
- Repository: 仓储模式
"""

from core.data.factory import BaseFactory
from core.data.builder import BaseBuilder, BuilderContext
from core.data.entity import BaseEntity, PydanticEntity
from core.data.strategy import BaseStrategy, StrategyResult
from core.data.repository import BaseRepository
from core.data.config import BaseConfig

__all__ = [
    'BaseFactory',
    'BaseBuilder',
    'BuilderContext',
    'BaseEntity',
    'PydanticEntity',
    'BaseStrategy',
    'StrategyResult',
    'BaseRepository',
    'BaseConfig',
]
```

#### 步骤 2.3：迁移文件内容

**factory.py**（原 baseFactory.py）：
```python
# -*- coding: utf-8 -*-
"""Factory 基类 - SQLAlchemy 版本"""
import factory
from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    """Factory 基类 - 自动保存到数据库"""

    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """延迟获取数据库会话"""
        if not hasattr(cls, 'Meta'):
            cls.Meta = type('Meta', (), {})
        
        if not hasattr(cls.Meta, 'sqlalchemy_session') or cls.Meta.sqlalchemy_session is None:
            try:
                from auto_tests.bdd_api_mock.config import get_config
                config = get_config()
                cls.Meta.sqlalchemy_session = config.SessionLocal()
            except ImportError:
                try:
                    from auto_tests.qfei_contract_api.config import settings
                    cls.Meta.sqlalchemy_session = settings.SessionLocal()
                except ImportError:
                    raise ImportError("无法导入项目配置")
        
        return super()._create(model_class, *args, **kwargs)
```

**builder.py**（合并 base_builder.py + BuilderContext）：
```python
# -*- coding: utf-8 -*-
"""Builder 基类和上下文"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.data.entity import BaseEntity


class BuilderContext:
    """Builder执行上下文"""

    def __init__(
        self,
        strategy: Optional[Any] = None,
        cascade_cleanup: bool = False,
        auto_prepare_deps: bool = True
    ):
        self.strategy = strategy
        self.cascade_cleanup = cascade_cleanup
        self.auto_prepare_deps = auto_prepare_deps
        self._created_entities: Dict[str, List[tuple]] = {}
        self._resolved_deps: Dict[str, 'BaseEntity'] = {}
        self._builder_registry: Dict[str, 'BaseBuilder'] = {}

    def track(self, entity_type: str, entity_id: Any, builder: 'BaseBuilder'):
        """追踪创建的实体"""
        if entity_type not in self._created_entities:
            self._created_entities[entity_type] = []
        self._created_entities[entity_type].append((entity_id, builder))

    def get_resolved_dep(self, dep_type: str) -> Optional['BaseEntity']:
        """获取已解决的依赖"""
        return self._resolved_deps.get(dep_type)

    def set_resolved_dep(self, dep_type: str, entity: 'BaseEntity'):
        """设置已解决的依赖"""
        self._resolved_deps[dep_type] = entity

    def register_builder(self, builder_type: str, builder: 'BaseBuilder'):
        """注册Builder"""
        self._builder_registry[builder_type] = builder

    def get_builder(self, builder_type: str) -> Optional['BaseBuilder']:
        """获取已注册的Builder"""
        return self._builder_registry.get(builder_type)

    def get_all_created(self) -> Dict[str, List[tuple]]:
        """获取所有创建的实体"""
        return self._created_entities.copy()


class BaseBuilder(ABC):
    """Builder 基类"""
    DEPENDENCIES: List[str] = []

    def __init__(self, context: Optional[BuilderContext] = None):
        self.context = context or BuilderContext()

    @abstractmethod
    def build(self, **kwargs) -> Any:
        """构建实体"""
        pass

    def prepare_dependencies(self) -> Dict[str, Any]:
        """准备依赖"""
        deps = {}
        for dep_type in self.DEPENDENCIES:
            resolved = self.context.get_resolved_dep(dep_type)
            if resolved:
                deps[dep_type] = resolved
        return deps
```

**entity.py**（合并 base_entity.py + pydantic_base.py）：
```python
# -*- coding: utf-8 -*-
"""实体基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class BaseEntity(ABC):
    """实体基类 - 传统 ORM 版本"""
    
    @property
    @abstractmethod
    def id(self) -> Any:
        """实体唯一标识"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """从字典创建"""
        pass


class PydanticEntity(BaseModel):
    """Pydantic 实体基类"""
    
    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'

    def to_api_payload(self) -> Dict[str, Any]:
        """转换为 API 请求体"""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'PydanticEntity':
        """从 API 响应创建"""
        return cls(**data)
```

**strategy.py**（合并 base_strategy.py + StrategyResult）：
```python
# -*- coding: utf-8 -*-
"""策略基类和结果"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.data.entity import BaseEntity


@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    entity: Optional['BaseEntity'] = None
    entities: Optional[List['BaseEntity']] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        return self.raw_data

    def get_entity(self) -> Optional['BaseEntity']:
        return self.entity

    def get_entities(self) -> List['BaseEntity']:
        return self.entities or []


class BaseStrategy(ABC):
    """策略基类"""

    @abstractmethod
    def create(self, entity_type: type, **kwargs) -> StrategyResult:
        """创建实体"""
        pass

    @abstractmethod
    def cleanup(self, entity: 'BaseEntity') -> bool:
        """清理实体"""
        pass
```

**repository.py**（原 repository_base.py）：
```python
# -*- coding: utf-8 -*-
"""仓储基类"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseRepository(ABC):
    """仓储基类 - 数据访问抽象"""

    def __init__(self, session=None):
        self.session = session

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[Any]:
        """根据ID获取"""
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        """获取所有"""
        pass

    @abstractmethod
    def create(self, **kwargs) -> Any:
        """创建"""
        pass

    @abstractmethod
    def update(self, id: Any, **kwargs) -> bool:
        """更新"""
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """删除"""
        pass
```

**config.py**（原 base/config.py）：
```python
# -*- coding: utf-8 -*-
"""配置基类"""
from abc import ABC
from typing import Any, Dict


class BaseConfig(ABC):
    """配置基类"""
    PROJECT_NAME: str = ""
    PROJECT_DISPLAY_NAME: str = ""
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DATABASE: str = ""
    
    # API 配置
    BASE_URL: str = ""
    TIMEOUT: int = 30
    
    # 测试配置
    AUTO_CLEANUP: bool = True
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """转换为字典"""
        return {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith('_') and not callable(v)
        }
```

---

### 阶段三：创建 testing/ 目录（中优先级）

#### 步骤 3.1：创建 testing/ 目录结构

```
core/testing/
├── __init__.py
├── layers.py         # 测试分层：UnitTest, IntegrationTest, E2ETest
├── context.py        # TestContext
└── reporting.py      # AllureAdapter + 增强器
```

#### 步骤 3.2：创建 core/testing/__init__.py

```python
# -*- coding: utf-8 -*-
"""
测试支持模块 - 提供测试分层、上下文和报告功能
"""

from core.testing.layers import UnitTest, IntegrationTest, E2ETest, TestLayerType
from core.testing.context import TestContext
from core.testing.reporting import AllureAdapter

__all__ = [
    'UnitTest',
    'IntegrationTest',
    'E2ETest',
    'TestLayerType',
    'TestContext',
    'AllureAdapter',
]
```

#### 步骤 3.3：迁移 layering_base.py 到 testing/layers.py

- 保留 `UnitTest`, `IntegrationTest`, `E2ETest` 类
- 保留 `TestLayerType` 枚举
- 保留 `TestCaseResult` 数据类

#### 步骤 3.4：迁移 TestContext 到 testing/context.py

- 从 `layering_base.py` 提取 `TestContext` 类
- 从 `layering_base.py` 提取 `EventExpectation` 类

#### 步骤 3.5：合并 reporting/ 到 testing/reporting.py

- 合并 `reporting/adapter.py` 内容
- 合并 `reporting/enhancers/lineage.py` 内容
- 合并 `reporting/enhancers/matrix.py` 内容
- 合并 `reporting/enhancers/state_machine.py` 内容

---

### 阶段四：简化 ui/ 目录（低优先级）

#### 步骤 4.1：合并 ui/ 文件

```
core/ui/
├── __init__.py
└── web.py            # 合并 web_base.py
```

---

### 阶段五：重命名 settings/ 为 config/（低优先级）

#### 步骤 5.1：重命名目录

```bash
mv core/settings core/config
```

#### 步骤 5.2：更新所有引用

```bash
# 查找所有引用
grep -r "from core.settings" --include="*.py" d:\code\MangoPytest\
grep -r "import core.settings" --include="*.py" d:\code\MangoPytest\
```

---

### 阶段六：更新 models/ 目录（已完成）

已完成的优化：
- ✅ 拆分为 api.py, config.py, lineage.py, strategy.py, testrun.py, variant.py
- ✅ 删除了 base.py, entity.py, result.py, other_model.py, ui_model.py

---

### 阶段七：更新导入路径（关键步骤）

#### 步骤 7.1：创建兼容性导入

在删除旧文件前，在 `__init__.py` 中保持向后兼容：

```python
# core/base/__init__.py (临时兼容层)
"""兼容性导入 - 请使用 core.data 替代"""
import warnings

warnings.warn(
    "core.base 模块已弃用，请使用 core.data",
    DeprecationWarning,
    stacklevel=2
)

from core.data.factory import BaseFactory
from core.data.builder import BaseBuilder, BuilderContext
from core.data.entity import BaseEntity, PydanticEntity
from core.data.strategy import BaseStrategy, StrategyResult
from core.data.repository import BaseRepository
from core.data.config import BaseConfig
```

#### 步骤 7.2：更新所有项目的导入

**需要更新的项目：**
- `auto_tests/api_mock/`
- `auto_tests/bdd_api_mock/`
- `auto_tests/pytest_api_mock/`
- `auto_tests/bdd_ui_mock/`
- `auto_tests/pytest_ui_mock/`

**更新示例：**
```python
# 旧导入
from core.base.baseFactory import BaseFactory
from core.base.base_builder import BaseBuilder
from core.base.builder_context import BuilderContext

# 新导入
from core.data import BaseFactory, BaseBuilder, BuilderContext
```

---

## 四、实施计划

### 第 1 周：准备阶段
- [ ] 创建重构分支 `refactor/core-structure`
- [ ] 运行完整测试套件，记录基线
- [ ] 验证 DAL 使用情况
- [ ] 验证未使用文件

### 第 2 周：核心重构
- [ ] 创建 `core/data/` 目录
- [ ] 迁移 base/ 文件到 data/
- [ ] 更新 models/strategy.py 引用
- [ ] 运行测试验证

### 第 3 周：测试模块重构
- [ ] 创建 `core/testing/` 目录
- [ ] 迁移 layering_base.py
- [ ] 合并 reporting/
- [ ] 运行测试验证

### 第 4 周：清理和优化
- [ ] 删除旧目录 base/, dal/
- [ ] 重命名 settings/ 为 config/
- [ ] 更新所有项目导入
- [ ] 运行完整测试套件
- [ ] 合并到主分支

---

## 五、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 导入路径变更导致测试失败 | 高 | 保持兼容性导入，逐步迁移 |
| DAL 被意外删除 | 中 | 彻底验证使用情况 |
| 循环导入 | 中 | 使用 TYPE_CHECKING 延迟导入 |
| 功能丢失 | 高 | 每步都运行测试验证 |

---

## 六、验证清单

### 重构前
- [ ] 所有测试通过
- [ ] 代码覆盖率基线记录
- [ ] 文档记录当前结构

### 重构后
- [ ] 所有测试通过
- [ ] 代码覆盖率不降低
- [ ] 导入路径更新完整
- [ ] 文档更新

---

## 七、附录

### A. 文件映射表

| 旧文件 | 新文件 | 操作 |
|--------|--------|------|
| core/base/baseFactory.py | core/data/factory.py | 迁移 |
| core/base/base_builder.py | core/data/builder.py | 合并 |
| core/base/builder_context.py | core/data/builder.py | 合并 |
| core/base/base_entity.py | core/data/entity.py | 合并 |
| core/base/pydantic_base.py | core/data/entity.py | 合并 |
| core/base/base_strategy.py | core/data/strategy.py | 合并 |
| core/base/strategy_result.py | core/data/strategy.py | 合并 |
| core/base/repository_base.py | core/data/repository.py | 迁移 |
| core/base/config.py | core/data/config.py | 迁移 |
| core/base/data_factory_base.py | - | 删除 |
| core/base/layering_base.py | core/testing/layers.py | 拆分 |
| core/base/pydantic_builder.py | - | 删除（未使用） |
| core/dal/ | - | 删除（如未使用） |
| core/reporting/adapter.py | core/testing/reporting.py | 合并 |
| core/reporting/enhancers/ | core/testing/reporting.py | 合并 |
| core/settings/ | core/config/ | 重命名 |
| core/ui/web_base.py | core/ui/web.py | 重命名 |

### B. 导入路径变更

| 旧导入 | 新导入 |
|--------|--------|
| `from core.base.baseFactory import BaseFactory` | `from core.data import BaseFactory` |
| `from core.base.base_builder import BaseBuilder` | `from core.data import BaseBuilder` |
| `from core.base.builder_context import BuilderContext` | `from core.data import BuilderContext` |
| `from core.base.base_entity import BaseEntity` | `from core.data import BaseEntity` |
| `from core.base.pydantic_base import PydanticEntity` | `from core.data import PydanticEntity` |
| `from core.base.base_strategy import BaseStrategy` | `from core.data import BaseStrategy` |
| `from core.base.strategy_result import StrategyResult` | `from core.data import StrategyResult` |
| `from core.base.repository_base import BaseRepository` | `from core.data import BaseRepository` |
| `from core.base.layering_base import UnitTest` | `from core.testing import UnitTest` |
| `from core.reporting.adapter import AllureAdapter` | `from core.testing import AllureAdapter` |
| `from core.settings.settings import Settings` | `from core.config.settings import Settings` |

---

*文档结束*
