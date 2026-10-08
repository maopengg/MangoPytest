# AI 元素定位使用指南

本文档说明本项目如何启用、观测与排查 AI 元素定位。设计背景与取舍见
[AI元素定位接入方案](../plans/AI元素定位接入方案.md)；提示词怎么写见
[AI 定位提示词编写规范](AI定位提示词编写规范.md)。

---

## 1. 它解决什么问题

元素的固定定位器（`定位方式` / `定位表达式`）失效时，mangoautomation 会进入**元素自愈**：

```text
固定定位重试窗口（默认 10s）耗尽
        ↓
本地确定性候选：历史记忆 → 快照基线 → 页面 DOM 文本/邻近节点
        ↓（都没命中）
AI 候选：把「元素描述 + 页面无障碍快照」交给模型，模型只返回快照节点的 ref
        ↓（命中后）
把 ref 派生成持久定位器 → 唯一性/可见性/语义校验 → 本次操作重试
```

**AI 只是自愈链路中的一环**：本地确定性候选先跑，命中就不调用模型（不产生费用）。

---

## 2. 默认状态与开关

| 项 | 默认值 | 说明 |
|---|---|---|
| `ELEMENT_HEALING_ENABLED` | `true` | 总开关。关闭后固定定位失败即失败，且**描述型元素无法执行** |
| `AI_ELEMENT_HEALING_ENABLED` | `false` | AI 开关。关闭时只跑本地自愈 |
| `AI_API_KEY` | `""` | **只允许环境变量 / CI Secret 注入**，禁止入库、禁止控制台录入 |
| `AI_BASE_URL` | `https://api.siliconflow.cn/v1` | 必须是 OpenAI 兼容网关 |
| `AI_MODEL` | `THUDM/GLM-Z1-9B-0414` | 模型名 |
| `AI_TIMEOUT` | `30` | 模型请求超时（秒）。**内部会被截断到最大 30s** |
| `AI_SEMANTIC_STRENGTH` | `0` | 语义强度。**0 = 最宽松**，值越大越严格（只影响两个语义豁免分支） |

统一配置在 `core/settings/settings.py`，可被项目 `.env.<env>`、环境变量、
以及 Web 控制台的运行参数覆盖（后写覆盖前写）。**Key 除外**：控制台已移除该字段。

### 启用方式

```bash
# 定向验证自愈靶场用例（推荐，成本最低）
AI_API_KEY=sk-xxx AI_ELEMENT_HEALING_ENABLED=true \
    ENV=test .venv/bin/python main.py --project pytest_ui -- -m ai_heal

# 全量开启（会改变用例结果，务必配合 §5 的双跑对比）
AI_API_KEY=sk-xxx AI_ELEMENT_HEALING_ENABLED=true \
    ENV=test .venv/bin/python main.py --project pytest_ui
```

---

## 3. 元素侧要提供什么

AI 读到的「元素描述」来自 **`ElementModel.elements[0].prompt`**，它由元素表的
3 组 `AI定位提示词` 列**按行合并**而来：

| 列 | 语义 | 必填 |
|---|---|---|
| `AI定位提示词1` | 控件描述（控件种类 + 区分特征） | 是 |
| `AI定位提示词2` | 所在区域 / 上下文 | 否 |
| `AI定位提示词3` | 排除项（`排除项：` 必须独占行首） | 否 |

> 历史背景：库侧 `first_prompt()` 只读第一个非空 `prompt`，所以逐 slot 分开填会让
> 第 2、3 列失效；项目在 `core/ui/element_runtime.py` 里统一合并到第 1 组。
> 写法细节与两个「语义反转」陷阱见[提示词编写规范](AI定位提示词编写规范.md)。

另外两项对 AI 有帮助的元数据由项目自动补齐：

- `category`：页面键映射成中文页面名（如 `componentsPage` → `组件演示页`）
- `element_version`：定位器 + 提示词的内容指纹，用于让旧自愈记录随配置变更失效

`说明` 列会在提示词为空时作为描述兜底（仅当长度 ≤ 60 字符，避免页面抓取文本混入）。

### 描述型元素（只有描述、没有定位器）

元素表只填 `AI定位提示词`、不填 `定位方式/表达式` 时，该元素为**描述型元素**：

- 库侧会合成占位定位组，**跳过固定定位阶段**直接进入自愈；
- 因此必须开启 `ELEMENT_HEALING_ENABLED`，否则 `ElementRuntime` 构造期直接报错并列出全部相关元素；
- 适用边界：稳定可见、语义明确的元素；**不适用**表格批量行内元素等靠序号的场景。

---

## 4. 如何观测

### 4.1 单条用例

发生自愈时会附加一个 **「AI 自愈」** Allure 附件，并在用例上打标签：

| 附件字段 | 含义 |
|---|---|
| `used_source` | `fixed_locator` / `ai_accessibility` / `ai_visual` / `candidate_exhausted` … |
| `used_ai` | 是否真的调用了模型 |
| `temporary_heal_used` | 是否临时采用了自愈结果 |
| `final_score` | 候选综合得分（临时采用阈值 85） |
| `decision` | 决策状态。**当前库版本只可能是 `temporary_heal` / `rejected`** |
| `reject_reasons` | 拒识原因（≤10 条） |
| `model` / `prompt_version` / `schema_version` | 模型与提示词版本 |
| `circuit_breaker` | 熔断状态 |
| `stages` | 各阶段耗时（memory / historical / candidates / agent / visual） |

标签：`healed=true`、`heal_source=<来源>`、`heal_mode=ai|local`、`heal_model=<模型>`。

### 4.2 整轮运行

会话结束时会把统计写入运行产物目录（`--alluredir` 的同级；直接跑 `main.py` 时写入
`artifacts/reports/`），文件名 `ai-healing-summary[-<worker>].json`，终端同时打印一行：

```text
[AI 自愈] 操作 N 次 · 触发自愈 M 次（AI A / 本地 L）· 自愈成功 S · 自愈后仍失败 F
```

Web 控制台的运行详情页有「AI 元素定位 / 自愈统计」面板（接口
`GET /api/runs/<id>/ai-healing`，自动合并多 worker 的汇总）。

---

## 5. 验收方式：双跑对比

**库侧没有"只建议不执行"的模式**：`WebElementHealingHarness._heal_mode()` 把模式
硬编码为 2（配置项仅为兼容保留），因此一旦开启 AI，被命中的元素会走
`TEMPORARY_HEAL` 并**重试操作、改变用例结果**。所以不能用"先观察再决定"的方式试水，
应改用双跑对比：

```bash
# 基线：AI 关闭
ENV=test .venv/bin/python main.py --project pytest_ui

# 对照：AI 开启
AI_API_KEY=sk-xxx AI_ELEMENT_HEALING_ENABLED=true \
    ENV=test .venv/bin/python main.py --project pytest_ui
```

对比两次的 pass/fail 集合：

- `基线失败 → AI 通过` = AI 救回的用例（收益，需人工确认不是"猜对"）
- `基线通过 → AI 失败` = AI 引入的回归（**必须为 0，否则关闭开关**）

---

## 6. 成本与约束

| 约束 | 值 | 位置 |
|---|---|---|
| 确定性候选预算 | 5s | 库 `policy/thresholds.py` |
| 模型单次超时 | ≤30s | 库 `AGENT_TIMEOUT_SECONDS` |
| 单候选验证超时 | 2s | 库 `CANDIDATE_TIMEOUT_SECONDS` |
| 候选总量 / AI 候选 | 24 / 5 | 库 `MAX_CANDIDATES` / `MAX_AGENT_CANDIDATES` |
| 熔断 | 连续 2 次失败 → 冷却 60s | 库 `AgentCircuitBreaker` |
| 鉴权类错误 | 直接全局冷却 | 同上（401 / invalid api key） |
| 历史记忆缓存 | `CACHE_TTL=60` | 库 harness |

**注意**：

1. 缓存的是**历史自愈记忆**，不是模型响应。TTL 内重复触发仍会真实调用模型。
2. 单次定位典型 1 次模型请求；最坏约 4 次（schema 修复 + 空响应重试 + `json_schema` 降级）。
3. 熔断器是**进程级类变量**，跨用例共享，键为 `(元素ID, 页面URL 去 #fragment)`。
4. AI 默认只对显式开启的运行生效；`-m ai_heal` 可只跑自愈靶场用例。

---

## 7. 排障

| 现象 | 原因与处理 |
|---|---|
| 日志出现「已请求启用但缺少凭据」 | `AI_ELEMENT_HEALING_ENABLED=true` 但 `AI_API_KEY` 为空。检查 Secret 注入 |
| 「未启用：ELEMENT_HEALING_ENABLED=false」 | 总开关被关闭；描述型元素此时还会在构造期报错 |
| 报「智能定位失败：AI 找到了相似元素，但与元素描述不一致」 | 候选被语义拒识。请补充更明确的控件种类/可见文案，参见编写规范 |
| 报「智能定位失败：…余额不足…」/「…熔断…」 | 网关额度或熔断；前者检查账户，后者等待冷却或检查模型配置 |
| 固定定位明明成功却仍报自愈失败文案 | 历史已知问题：库侧会把**操作级异常**（如文件不存在）也纳入重试与自愈并覆盖真实原因，见 `docs/guides/内部包升级记录.md` |
| 提示词写了但 AI 没反应 | 检查 `AI定位提示词1` 是否为模板串；执行 `python main.py --check-elements` |

---

## 8. 测试与回归

| 层次 | 位置 | 是否需要 Key |
|---|---|---|
| 提示词契约与体检 | `tests/test_prompt_spec.py` | 否 |
| 元素模型装配（合并/版本/回退） | `tests/test_ui_element_runtime.py` | 否 |
| 自愈统计与汇总 | `tests/test_healing_metrics.py` | 否 |
| 控制台统计接口 | `tests/test_web_console/test_ai_healing_api.py` | 否 |
| **AI 链路端到端（fake model client）** | `tests/test_ai_element_locating.py`（`-m ai_e2e`） | 否 |
| **真实网关冒烟** | `tests/test_ai_element_locating_smoke.py`（`-m ai_smoke`） | 是，默认跳过 |

```bash
# 跳过需要浏览器的端到端用例
ENV=test .venv/bin/python -m pytest tests -q -m "not ai_e2e"

# 真实网关冒烟（需注入 Key）
AI_API_KEY=sk-xxx ENV=test .venv/bin/python -m pytest \
    tests/test_ai_element_locating_smoke.py -q
```
