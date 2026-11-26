import { esc, formatDuration, statusText } from '../common/dom.js';
function renderEvidenceSummary(e, projectKind = '') {
  const auxiliaryCalls = Array.from({
      length: Math.max(e.requests?.length || 0, e.responses?.length || 0),
    }),
    uiOperations = groupUiOperations(e.operations || []),
    items =
      projectKind === 'ui'
        ? [
            ['case', 'Case', e.case],
            ['data', '数据', e.data],
            ['lineage', '血缘', e.lineage],
            ['auxiliary', '辅助接口', auxiliaryCalls],
            ['operations', 'UI 操作', uiOperations],
            ['logs', '日志', e.logs],
            ['screenshots', '截图', e.screenshots],
          ]
        : [
            ['case', 'Case', e.case],
            ['data', '数据', e.data],
            ['lineage', '血缘', e.lineage],
            ['requests', '请求', e.requests],
            ['responses', '响应', e.responses],
            ['operations', 'UI 操作', uiOperations],
            ['logs', '日志', e.logs],
            ['screenshots', '截图', e.screenshots],
          ],
    total = items.reduce((sum, [, , values]) => sum + (values?.length || 0), 0);
  return `<div class="evidence-summary" role="group" aria-label="结果信息筛选"><button type="button" class="evidence-chip active" aria-pressed="true" onclick="filterEvidence('all',this)">全部 <strong>${total}</strong></button>${items
    .map(
      ([kind, name, values]) =>
        `<button type="button" class="evidence-chip ${
          values?.length ? 'ready' : 'empty-evidence'
        }" aria-pressed="false" ${
          values?.length ? '' : 'disabled'
        } onclick="filterEvidence('${kind}',this)">${esc(name)} <strong>${
          values?.length || 0
        }</strong></button>`
    )
    .join('')}</div>`;
}
function evidenceKind(title) {
  return (
    {
      'Case 信息': 'case',
      测试数据: 'data',
      'API / 协议请求': 'requests',
      'API / 协议响应': 'responses',
      'UI 操作明细': 'operations',
      日志信息: 'logs',
      截图与现场: 'screenshots',
    }[title] || ''
  );
}
function filterEvidence(kind, button) {
  const detail = button.closest('.allure-case-detail');
  if (!detail) return;
  detail.querySelectorAll('.evidence-chip').forEach((chip) => {
    const active = chip === button;
    chip.classList.toggle('active', active);
    chip.setAttribute('aria-pressed', String(active));
  });
  detail.querySelectorAll('.filterable-evidence').forEach((section) => {
    const visible = kind === 'all' || section.dataset.evidenceKind === kind;
    section.hidden = !visible;
    if (visible && section.tagName === 'DETAILS')
      section.open = kind === 'all' ? section.dataset.defaultOpen === 'true' : true;
  });
}
function renderEvidenceSection(title, items, open = true) {
  const kind = evidenceKind(title);
  return items?.length
    ? `<details class="detail-section evidence-section filterable-evidence" data-evidence-kind="${kind}" data-default-open="${open}" ${
        open ? 'open' : ''
      }><summary><h3>${esc(title)}${
        items.length > 1 ? ` <span>${items.length}</span>` : ''
      }</h3></summary>${renderAttachments(items, true)}</details>`
    : '';
}
function renderLogSection(items = []) {
  if (!items.length) return '';
  return `<details class="detail-section evidence-section filterable-evidence log-section" data-evidence-kind="logs" data-default-open="false"><summary><h3>日志信息${
    items.length > 1 ? ` <span>${items.length}</span>` : ''
  }</h3></summary><div class="log-entries">${items
    .map(
      (item) =>
        `<section class="log-entry">${
          items.length > 1
            ? `<div class="log-entry-head"><strong>${esc(item.name || '日志')}</strong>${
                item.phase ? `<span>${esc(item.phase)}</span>` : ''
              }</div>`
            : ''
        }<pre class="log-content">${esc(item.content || '暂无可预览日志内容')}</pre></section>`
    )
    .join('')}</div></details>`;
}
const uiOperationLabels = {
  w_goto: '打开页面',
  w_wait_for_load_state: '等待页面加载',
  w_click: '点击元素',
  w_dblclick: '双击元素',
  w_force_click: '强制点击元素',
  w_input: '输入内容',
  w_type: '逐字输入',
  w_clear: '清空内容',
  w_clear_input: '清空输入框',
  w_hover: '悬停元素',
  w_get_text: '读取文本',
  w_upload_files: '上传文件',
  w_download: '下载文件',
  w_scroll_to_element: '滚动到元素',
  w_right_click: '右键点击元素',
  w_drag_to: '拖拽元素',
  w_press: '键盘按键',
  w_press_sequentially: '连续按键',
  w_focus: '聚焦元素',
  w_blur: '取消聚焦',
  w_check: '勾选元素',
  w_uncheck: '取消勾选',
  w_set_checked: '设置选中状态',
  w_select_option: '选择下拉选项',
  w_ele_screenshot: '元素截图',
};
function groupUiOperations(items = []) {
  const groups = [];
  items.forEach((item) => {
    const isInput = item.name === '操作信息',
      context = item.context || '',
      candidate = [...groups].reverse().find((group) => group.context === context && !group.result);
    if (isInput)
      groups.push({
        context,
        input: item,
        result: null,
      });
    else if (item.name === '操作结果' && candidate) candidate.result = item;
    else
      groups.push({
        context,
        input: isInput ? item : null,
        result: isInput ? null : item,
      });
  });
  return groups;
}
function uiOperationName(group) {
  const method =
    group.input?.data?.operation || String(group.context || '').replace(/^UI 操作 ·\s*/, '') || 'unknown';
  return {
    method,
    label: uiOperationLabels[method] || `执行 ${method.replace(/^w_/, '').replaceAll('_', ' ')}`,
  };
}
function uiOperationTarget(group) {
  const input = group.input?.data || {},
    named = input.named_elements?.[0]?.name,
    value =
      named ??
      input.arguments?.[0] ??
      input.keyword_arguments?.locator ??
      input.keyword_arguments?.text ??
      '';
  return value === null || typeof value === 'object' ? '' : String(value);
}
function renderUiOperations(items = []) {
  const groups = groupUiOperations(items);
  if (!groups.length) return '';
  return `<details class="detail-section evidence-section filterable-evidence ui-operation-section" data-evidence-kind="operations" data-default-open="true" open><summary><h3>UI 操作明细 <span>${
    groups.length
  }</span></h3></summary><div class="ui-operation-list">${groups
    .map((group, index) => {
      const { method, label } = uiOperationName(group),
        result = group.result?.data || {},
        status = result.status || 'unknown',
        target = uiOperationTarget(group);
      return `<details class="ui-operation-row"><summary><span class="ui-operation-index">${
        index + 1
      }</span><span class="ui-operation-main"><strong>${esc(label)}</strong><code>${esc(method)}</code>${
        target ? `<small>${esc(target)}</small>` : ''
      }</span><span class="ui-operation-status ${esc(status)}">${esc(
        statusText[status] || status
      )}</span><span class="ui-operation-duration">${
        result.duration_ms === undefined ? '—' : formatDuration(result.duration_ms)
      }</span></summary><div class="ui-operation-detail"><section><h4>操作输入</h4>${
        group.input?.data
          ? renderJsonTree(group.input.data, 0, true)
          : '<span class="muted">未记录操作输入</span>'
      }</section><section><h4>执行结果</h4>${
        group.result?.data
          ? renderJsonTree(group.result.data, 0, true)
          : '<span class="muted">未记录执行结果</span>'
      }</section></div></details>`;
    })
    .join('')}</div></details>`;
}
function renderAuxiliaryApiSection(requests = [], responses = []) {
  const count = Math.max(requests.length, responses.length);
  if (!count) return '';
  const calls = Array.from(
    {
      length: count,
    },
    (_, index) => {
      const request = requests[index],
        response = responses[index],
        context = request?.context || response?.context || `调用 ${index + 1}`,
        phase = request?.phase || response?.phase || '';
      return `<section class="auxiliary-api-call"><div class="auxiliary-api-call-head"><strong>${esc(
        context
      )}</strong>${phase ? `<span>${esc(phase)}</span>` : ''}</div>${renderAttachments(
        [request, response].filter(Boolean),
        true
      )}</section>`;
    }
  ).join('');
  return `<details class="detail-section evidence-section filterable-evidence auxiliary-api-section" data-evidence-kind="auxiliary" data-default-open="false"><summary><h3>辅助接口调用 <span>${count}</span></h3></summary><p class="evidence-note">用于测试数据准备、身份登录、后端校验或清理，不代表该用例属于 API 自动化。</p>${calls}</details>`;
}
function renderCollapsibleSection(title, content, count = 0, open = false) {
  return `<details class="detail-section evidence-section" ${open ? 'open' : ''}><summary><h3>${esc(
    title
  )} <span>${count}</span></h3></summary>${content}</details>`;
}
function renderParameters(items) {
  return `<table class="detail-table">${items
    .map((x) => `<tr><td>${esc(x.name)}</td><td>${esc(x.value)}</td></tr>`)
    .join('')}</table>`;
}
function renderError(details) {
  return `<div class="detail-section error-box"><strong>${esc(details.message || '执行失败')}</strong>${
    details.trace ? `<pre>${esc(details.trace)}</pre>` : ''
  }</div>`;
}
function renderSteps(items) {
  return items
    .map(
      (x) =>
        `<div class="step"><div class="step-head"><i class="case-status-icon ${esc(
          x.status
        )}"></i><strong>${esc(x.name)}</strong><span class="case-duration">${formatDuration(
          x.duration_ms
        )}</span></div><div class="step-body">${x.parameters.length ? renderParameters(x.parameters) : ''}${
          x.status_details.message || x.status_details.trace ? renderError(x.status_details) : ''
        }${x.attachments.length ? renderAttachments(x.attachments) : ''}${
          x.steps.length ? renderSteps(x.steps) : ''
        }</div></div>`
    )
    .join('');
}
function jsonPrimitive(value) {
  if (value === null) return '<span class="json-null">null</span>';
  if (typeof value === 'boolean') return `<span class="json-boolean">${value}</span>`;
  if (typeof value === 'number') return `<span class="json-number">${value}</span>`;
  return `<span class="json-string">${esc(value)}</span>`;
}
const internalKeyLabels = {
  name: '名称',
  display_name: '展示名称',
  case_id: '用例 ID',
  node_id: 'Pytest 节点',
  file: '测试文件',
  line: '代码行号',
  markers: '测试标签',
  description: '用例描述',
  parameters: '参数化数据',
  fixtures: 'Fixture 依赖',
  operation: '操作名称',
  arguments: '位置参数',
  keyword_arguments: '关键字参数',
  named_elements: '元素仓库信息',
  project_name: '项目名称',
  module_name: '模块名称',
  page_name: '页面名称',
  locators: '定位器',
  slot: '定位顺序',
  expression: '定位表达式',
  index: '元素下标',
  ai_prompt: 'AI 定位提示词',
  element_result: '元素执行结果',
  elements: '元素现场',
  element_reference: '元素引用',
  reference: '元素编号',
  source: '参数来源',
  locator: '实际定位器',
  match_count: '匹配数量',
  element: '元素快照',
  tag_name: '标签名称',
  text: '元素文本',
  value: '元素值',
  attributes: '元素属性',
  visible: '是否可见',
  enabled: '是否可用',
  editable: '是否可编辑',
  bounding_box: '元素坐标',
  snapshot_error: '快照错误',
  x: '横坐标 X',
  y: '纵坐标 Y',
  width: '宽度',
  height: '高度',
  status: '执行状态',
  duration_ms: '耗时（毫秒）',
  return_value: '返回值',
  page_url: '页面地址',
  error_type: '异常类型',
  error: '错误信息',
  protocol: '协议类型',
  method: '请求方法',
  url: '请求地址',
  headers: '请求头',
  elapsed_ms: '耗时（毫秒）',
  body: '响应体',
  query: '连接参数',
  expected_type: '预期消息类型',
  limit: '最大接收次数',
  payload: '消息体',
  stream: '流式响应',
  message_count: '消息数量',
  kind: '节点类型',
  label: '节点名称',
  entity_type: '实体类型',
  entity_id: '实体 ID',
};
function internalKeyLabel(key) {
  return internalKeyLabels[key] || key;
}
function renderJsonTree(value, depth = 0, translateKeys = true) {
  if (value === null || typeof value !== 'object') return jsonPrimitive(value);
  const entries = Array.isArray(value) ? value.map((item, index) => [index, item]) : Object.entries(value);
  if (!entries.length) return `<span class="json-empty">${Array.isArray(value) ? '[]' : '{}'}</span>`;
  return `<div class="json-tree depth-${depth}">${entries
    .map(([key, item]) => {
      const complex = item !== null && typeof item === 'object',
        count = complex ? (Array.isArray(item) ? item.length : Object.keys(item).length) : 0,
        label = translateKeys ? internalKeyLabel(key) : key;
      return `<div class="json-row ${complex ? 'complex' : ''}"><span class="json-key">${esc(
        label
      )}</span><div class="json-value">${
        complex
          ? `<details ${depth < 1 ? 'open' : ''}><summary>${
              Array.isArray(item) ? '数组' : '对象'
            } · ${count} 项</summary>${renderJsonTree(item, depth + 1, translateKeys)}</details>`
          : jsonPrimitive(item)
      }</div></div>`;
    })
    .join('')}</div>`;
}
function renderJsonSection(title, value, open = true, translateKeys = true) {
  if (value === undefined) return '';
  return `<details class="json-section" ${open ? 'open' : ''}><summary><strong>${esc(title)}</strong><span>${
    value !== null && typeof value === 'object'
      ? (Array.isArray(value) ? value.length : Object.keys(value).length) + ' 项'
      : ''
  }</span></summary>${renderJsonTree(value, 0, translateKeys)}</details>`;
}
function renderPayload(title, value) {
  if (value === undefined || value === null) return '';
  const content = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  return `<section class="payload-section"><strong>${esc(title)}</strong><pre class="json-payload">${esc(
    content
  )}</pre></section>`;
}
function requestFieldTitle(key) {
  return (
    {
      params: '查询参数 Params',
      json: '请求体 JSON',
      data: '请求数据 Data',
      files: '上传文件 Files',
      payload: '消息体 Payload',
      query: '连接参数 Query',
      follow_redirects: '重定向设置',
    }[key] || key
  );
}
function exchangeContext(item) {
  const context = String(item.context || '').replace(/^HTTP\s+/i, ''),
    phase = item.phase ? `${item.phase} · ` : '';
  return context ? `${phase}${context}` : phase.replace(/ · $/, '');
}
function renderStructuredAttachment(item) {
  const data = item.data;
  if (data === null || typeof data !== 'object') return renderJsonTree(data);
  const name = String(item.name || ''),
    isResponse = name.includes('响应信息'),
    isRequest = name.includes('请求信息'),
    context = exchangeContext(item);
  if (isResponse) {
    const status = data.status ?? '—',
      statusClass =
        Number(status) >= 200 && Number(status) < 400 ? 'ok' : Number(status) >= 400 ? 'bad' : 'neutral';
    return `<div class="exchange-summary"><span class="exchange-kind">响应</span>${
      context ? `<code class="exchange-context">${esc(context)}</code>` : ''
    }<span class="http-status ${statusClass}">${esc(status)}</span>${
      data.elapsed_ms !== null && data.elapsed_ms !== undefined
        ? `<span class="exchange-duration">${esc(data.elapsed_ms)} ms</span>`
        : ''
    }</div>${renderJsonSection('响应头 Headers', data.headers, false, false)}${renderPayload(
      '响应体 Body',
      data.body
    )}`;
  }
  if (isRequest) {
    return `<div class="exchange-summary"><span class="exchange-kind">${esc(data.protocol || '请求')}</span>${
      data.method ? `<span class="http-method">${esc(data.method)}</span>` : ''
    }${context ? `<code class="exchange-context">${esc(context)}</code>` : ''}${
      data.url ? `<code class="exchange-url">${esc(data.url)}</code>` : ''
    }</div>${
      data.headers ? renderJsonSection('请求头 Headers', data.headers, false, false) : ''
    }${Object.entries(data)
      .filter(
        ([key, value]) =>
          !['protocol', 'method', 'url', 'headers'].includes(key) && value !== null && value !== undefined
      )
      .map(([key, value]) => renderPayload(requestFieldTitle(key), value))
      .join('')}`;
  }
  return renderJsonTree(data);
}
function renderAttachments(items, compact = false) {
  return `<div class="attachment-grid">${items
    .map((x) => {
      const path = x.source.split('/').map(encodeURIComponent).join('/'),
        url = `/api/runs/${window.runId}/preview/${path}`,
        structured = x.data !== null && x.data !== undefined;
      return `<div class="attachment ${structured ? 'structured-attachment' : ''} ${
        compact ? 'compact-attachment' : ''
      }">${
        compact
          ? ''
          : `<div class="attachment-head"><strong>${esc(x.name)}</strong></div><small>${esc(x.type)} · ${
              x.size
            } B</small>`
      }${
        x.type.startsWith('image/')
          ? `<img src="${url}" alt="${esc(x.name)}">`
          : structured
          ? `<div class="structured-json">${renderStructuredAttachment(x)}</div>${
              x.content
                ? `<details class="raw-json"><summary>查看原始 JSON</summary><pre class="attachment-text">${esc(
                    x.content
                  )}</pre></details>`
                : ''
            }`
          : x.content
          ? `<details><summary>查看内容</summary><pre class="attachment-text">${esc(
              x.content
            )}</pre></details>`
          : ''
      }</div>`;
    })
    .join('')}</div>`;
}
export {
  filterEvidence,
  renderAttachments,
  renderAuxiliaryApiSection,
  renderCollapsibleSection,
  renderError,
  renderEvidenceSection,
  renderEvidenceSummary,
  renderJsonSection,
  renderLogSection,
  renderParameters,
  renderSteps,
  renderUiOperations,
};
