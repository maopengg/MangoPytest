# Core 模块审计

本次审计以 Python 静态引用、包导入链和根测试为依据。

## 已清理

| 原模块 | 结论 | 处理 |
|---|---|---|
| `core/bdd` | 新 BDD 项目已使用项目内 Steps + `core/dal`，无运行时引用 | 删除 |
| `core/lineage` | 旧数据血缘实验，无运行时引用 | 删除 |
| `core/testing` | 旧测试分层实验，无运行时引用 | 删除 |
| `core/reporting` | 只有 Allure 基础适配器仍被使用 | 适配器迁至 `core/utils/allure.py`，其余删除 |
| `core/utils/main_run.py` | 已由根 `main.py` 的隔离子进程入口替代 | 删除 |
| `core/utils/notice.py`、`zip_files.py` | 仅被旧 MainRun 使用 | 删除 |

## 保留

`core/settings`、`core/sources`、`core/enums`、`core/models`、`core/exceptions` 和
`core/decorators` 虽未出现在简化的目录示意中，但仍有真实运行时消费者，因此保留。
后续只有在完成调用方迁移和兼容期设计后才应继续合并，不能仅凭静态目录外观删除。

验证基线：根 `pytest.ini` 只收集 `tests/` 下的 Core 测试；各 Demo 通过
`main.py --project ...` 使用各自的 pytest rootdir 独立收集。
