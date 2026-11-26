import { esc, formatDuration, formatTime, statusText } from '../common/dom.js';
import {
  renderAttachments,
  renderAuxiliaryApiSection,
  renderCollapsibleSection,
  renderError,
  renderEvidenceSection,
  renderEvidenceSummary,
  renderLogSection,
  renderParameters,
  renderSteps,
  renderUiOperations,
} from './evidence.js';
import { renderLineageSection } from './lineage.js';
let allureTests = [],
  activeAllureCaseId = '',
  activeRunProjectId = '',
  activeRunProjectKind = '';
function renderAllure(report, context = {}) {
  activeRunProjectId = context.projectId || '';
  activeRunProjectKind = context.projectKind || '';
  allureTests = report.tests || [];
  const overview = document.getElementById('allure-overview');
  if (!report.available) {
    overview.innerHTML = '<div class="allure-unavailable">正在等待 Allure 结构化结果…</div>';
    document.getElementById('allure-case-list').innerHTML = '<div class="empty">暂无测试结果</div>';
    return;
  }
  const s = report.summary,
    total = s.total || 1,
    p = Math.round((s.passed / total) * 360),
    f = p + Math.round((s.failed / total) * 360),
    b = f + Math.round((s.broken / total) * 360);
  overview.innerHTML = `<div class="status-donut" style="background:conic-gradient(#2e9b63 0 ${p}deg,#d14343 ${p}deg ${f}deg,#e49628 ${f}deg ${b}deg,#9aa29c ${b}deg 360deg)"><div class="donut-value"><strong>${
    s.total
  }</strong><span>测试用例</span></div></div><div class="overview-copy"><h2>执行概览</h2><p>${formatTime(
    s.start
  )} · 总耗时 ${formatDuration(s.duration_ms)}</p><div class="status-breakdown">${[
    'passed',
    'failed',
    'broken',
    'skipped',
  ]
    .map(
      (k) =>
        `<span class="status-chip"><i class="status-dot ${k}"></i>${statusText[k]} <strong>${
          s[k] || 0
        }</strong></span>`
    )
    .join('')}</div></div>`;
  filterAllureCases();
  const preferred = allureTests.find((x) => ['failed', 'broken'].includes(x.status)) || allureTests[0];
  if (preferred) selectAllureCase(preferred.id);
}
function allureHierarchyParts(item, mode) {
  if (mode === 'suite') {
    const folders = String(item.parent_suite || '')
        .split(/[./\\]+/)
        .map((x) => x.trim())
        .filter(Boolean)
        .map((name) => ({
          name,
          kind: 'folder',
        })),
      files = String(item.suite || '')
        .split(/[./\\]+/)
        .map((x) => x.trim())
        .filter(Boolean)
        .map((name) => ({
          name,
          kind: 'file',
        }));
    return [...folders, ...files].length
      ? [...folders, ...files]
      : [
          {
            name: '未分类',
            kind: 'file',
          },
        ];
  }
  const parts = [
    {
      name: activeRunProjectId || '未命名项目',
      kind: 'project',
    },
  ];
  if (item.epic)
    parts.push({
      name: item.epic,
      kind: 'epic',
    });
  if (item.feature)
    parts.push({
      name: item.feature,
      kind: 'feature',
    });
  if (item.story)
    parts.push({
      name: item.story,
      kind: 'story',
    });
  if (parts.length === 1)
    parts.push({
      name: '未分类',
      kind: 'feature',
    });
  return parts;
}
function buildAllureSuiteTree(items, mode) {
  const root = {
    name: '',
    kind: 'root',
    children: new Map(),
    cases: [],
    count: 0,
  };
  items.forEach((item) => {
    let node = root;
    node.count++;
    allureHierarchyParts(item, mode).forEach((part) => {
      const key = `${part.kind}:${part.name}`;
      if (!node.children.has(key))
        node.children.set(key, {
          ...part,
          children: new Map(),
          cases: [],
          count: 0,
        });
      node = node.children.get(key);
      node.count++;
    });
    node.cases.push(item);
  });
  return root;
}
function hierarchyKindLabel(kind) {
  return (
    {
      project: '项目',
      epic: 'Epic',
      feature: 'Feature',
      story: 'Story',
      folder: '目录',
      file: '文件',
    }[kind] || ''
  );
}
function allureCaseRow(item) {
  return `<button type="button" class="allure-case-row" data-id="${esc(
    item.id
  )}" onclick="selectAllureCase(this.dataset.id)"><i class="case-status-icon ${esc(
    item.status
  )}"></i><span><strong>${esc(item.name)}</strong><small>${esc(
    item.story || item.feature || item.full_name
  )}</small></span><span class="case-duration">${formatDuration(item.duration_ms)}</span></button>`;
}
function renderAllureTreeNode(node, depth, expandAll) {
  const children = [...node.children.values()]
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((child) => renderAllureTreeNode(child, depth + 1, expandAll))
      .join(''),
    cases = node.cases.map(allureCaseRow).join(''),
    leafNode = node.cases.length > 0,
    open = expandAll || depth === 0 ? 'open' : '';
  return `<details class="allure-tree-node kind-${esc(node.kind)} ${
    leafNode ? 'leaf-node' : ''
  }" ${open}><summary><span class="allure-tree-icon" aria-hidden="true"></span><span>${esc(
    node.name
  )}</span><small>${hierarchyKindLabel(node.kind)}</small><strong>${
    node.count
  }</strong></summary><div class="allure-tree-children">${children}${cases}</div></details>`;
}
function revealAllureCaseRow(id) {
  const row = [...document.querySelectorAll('.allure-case-row')].find((element) => element.dataset.id === id);
  if (!row) return;
  row.classList.add('active');
  let parent = row.parentElement;
  while (parent) {
    if (parent.tagName === 'DETAILS') parent.open = true;
    parent = parent.parentElement;
  }
}
function filterAllureCases() {
  const search = (document.getElementById('allure-search')?.value || '').toLowerCase(),
    status = document.getElementById('allure-status')?.value || '',
    mode = document.getElementById('allure-group-mode')?.value || 'behavior',
    items = allureTests.filter(
      (x) =>
        (!status || x.status === status) &&
        (!search ||
          x.name.toLowerCase().includes(search) ||
          x.full_name.toLowerCase().includes(search) ||
          x.tags.some((t) => t.toLowerCase().includes(search)))
    ),
    target = document.getElementById('allure-case-list');
  target.innerHTML = items.length
    ? `<div class="allure-suite-tree">${[...buildAllureSuiteTree(items, mode).children.values()]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((node) => renderAllureTreeNode(node, 0, Boolean(search)))
        .join('')}</div>`
    : '<div class="empty">没有匹配的用例</div>';
  if (activeAllureCaseId) revealAllureCaseRow(activeAllureCaseId);
}
function selectAllureCase(id) {
  const item = allureTests.find((x) => x.id === id);
  if (!item) return;
  activeAllureCaseId = id;
  document
    .querySelectorAll('.allure-case-row')
    .forEach((x) => x.classList.toggle('active', x.dataset.id === id));
  revealAllureCaseRow(id);
  const hierarchy = [item.epic, item.feature, item.story].filter(Boolean),
    labels = [...hierarchy, ...item.tags, item.severity ? `severity: ${item.severity}` : ''].filter(Boolean),
    e = item.evidence || {},
    evidenceSources = new Set(
      Object.values(e)
        .flat()
        .map((x) => x.source)
    ),
    otherAttachments = item.attachments.filter((x) => !evidenceSources.has(x.source)),
    fixtureSteps = [...item.fixtures.befores, ...item.fixtures.afters],
    protocolEvidence =
      activeRunProjectKind === 'ui'
        ? renderAuxiliaryApiSection(e.requests, e.responses)
        : renderEvidenceSection('API / 协议请求', e.requests) +
          renderEvidenceSection('API / 协议响应', e.responses);
  document.getElementById(
    'allure-case-detail'
  ).innerHTML = `<div class="case-detail-head"><div><span class="status-label ${esc(item.status)}">${esc(
    statusText[item.status] || item.status
  )}</span><h2>${esc(item.name)}</h2><p>${esc(
    item.full_name
  )}</p></div><div class="case-duration">${formatDuration(item.duration_ms)}<br>${formatTime(
    item.start
  )}</div></div>${renderEvidenceSummary(e, activeRunProjectKind)}${
    item.description ? `<div class="detail-section"><h3>描述</h3><p>${esc(item.description)}</p></div>` : ''
  }${
    labels.length
      ? `<div class="detail-section"><h3>分类与标签</h3><div class="detail-badges">${labels
          .map((x) => `<span class="detail-badge">${esc(x)}</span>`)
          .join('')}</div></div>`
      : ''
  }${renderEvidenceSection('Case 信息', e.case, false)}${renderEvidenceSection(
    '测试数据',
    e.data,
    false
  )}${renderLineageSection(e.lineage)}${
    item.parameters.length
      ? `<div class="detail-section"><h3>参数化数据</h3>${renderParameters(item.parameters)}</div>`
      : ''
  }${
    item.status_details.message || item.status_details.trace ? renderError(item.status_details) : ''
  }${protocolEvidence}${renderUiOperations(e.operations)}${renderLogSection(e.logs)}${renderEvidenceSection(
    '截图与现场',
    e.screenshots
  )}${renderCollapsibleSection(
    '完整执行步骤',
    item.steps.length ? renderSteps(item.steps) : '<p class="muted">该用例尚未记录显式 allure.step。</p>',
    item.steps.length
  )}${
    fixtureSteps.length
      ? renderCollapsibleSection('Fixture 前后置', renderSteps(fixtureSteps), fixtureSteps.length)
      : ''
  }${
    otherAttachments.length
      ? renderCollapsibleSection('其他附件', renderAttachments(otherAttachments), otherAttachments.length)
      : ''
  }`;
}
export { filterAllureCases, renderAllure, selectAllureCase };
