import { api } from '../common/api.js';
import { esc, setButtonLoading, toast } from '../common/dom.js';
let allCases = [],
  selectedFile = '',
  selectedFileExecutable = false,
  selectedFileExecutionKind = '',
  selectedFileExecutionTarget = '',
  selectedFileCollectionState = '',
  selectedSource = '',
  sourceLoading = false,
  sourceError = '';
async function loadProjectCases() {
  try {
    const [tree, cases] = await Promise.all([
      api(`/api/projects/${window.projectId}/tree`),
      api(`/api/projects/${window.projectId}/cases`),
    ]);
    allCases = cases;
    document.getElementById('case-count').textContent = `${cases.length} 条用例`;
    document.getElementById('file-tree').innerHTML = tree.length
      ? renderFileTree(tree)
      : '<div class="empty">没有可展示文件</div>';
    const marks = [...new Set(cases.flatMap((c) => c.markers))].sort();
    document.getElementById('mark-filter').innerHTML =
      '<option value="">全部标签</option>' + marks.map((m) => `<option>${esc(m)}</option>`).join('');
    await selectInitialProjectFile(tree);
  } catch (e) {
    toast(e.message);
  }
}
function buildFileTree(items) {
  const root = {
    name: '',
    path: '',
    folders: new Map(),
    files: [],
    count: 0,
  };
  items.forEach((file) => {
    const parts = file.path.split('/'),
      name = parts.pop();
    let node = root;
    parts.forEach((part) => {
      if (!node.folders.has(part)) {
        const path = node.path ? `${node.path}/${part}` : part;
        node.folders.set(part, {
          name: part,
          path,
          folders: new Map(),
          files: [],
          count: 0,
        });
      }
      node = node.folders.get(part);
    });
    node.files.push({
      ...file,
      name,
    });
  });
  function total(node) {
    node.count = node.files.reduce((sum, file) => sum + (file.count || 0), 0);
    node.folders.forEach((folder) => (node.count += total(folder)));
    return node.count;
  }
  total(root);
  return root;
}
function fileTreeIcon(type) {
  return `<span class="tree-file-icon ${type === 'feature' ? 'feature' : 'python'}" aria-hidden="true">${
    type === 'feature' ? 'F' : 'PY'
  }</span>`;
}
function fileTreeButton(file) {
  const state =
    file.collection_state === 'not_collected' ? '<span class="file-state not-collected">未收集</span>' : '';
  return `<button type="button" class="file-item" data-path="${esc(file.path)}" data-executable="${
    file.executable
  }" data-execution-kind="${esc(file.execution_kind || '')}" data-execution-target="${esc(
    file.execution_target || ''
  )}" data-collection-state="${esc(file.collection_state || 'source')}" title="${esc(
    file.path
  )}" onclick="selectFile(this.dataset.path,this.dataset.executable==='true',this.dataset.executionKind,this.dataset.executionTarget,this.dataset.collectionState,this)">${fileTreeIcon(
    file.type
  )}<span class="tree-label">${esc(file.name)}</span>${state}${
    file.count ? `<span class="file-count">${file.count}</span>` : ''
  }</button>`;
}
function renderFileTree(items) {
  const root = buildFileTree(items);
  function folderHtml(folder, depth) {
    const folders = [...folder.folders.values()].sort((a, b) => a.name.localeCompare(b.name)),
      files = folder.files.sort((a, b) => a.name.localeCompare(b.name)),
      children = [...folders.map((child) => folderHtml(child, depth + 1)), ...files.map(fileTreeButton)].join(
        ''
      );
    return `<details class="file-folder" ${
      folder.count > 0 ? 'open' : ''
    }><summary><span class="folder-icon" aria-hidden="true"></span><span class="tree-label">${esc(
      folder.name
    )}</span>${
      folder.count ? `<span class="file-count">${folder.count}</span>` : ''
    }</summary><div class="tree-children">${children}</div></details>`;
  }
  return `<div class="tree-root">${[...root.folders.values()]
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((folder) => folderHtml(folder, 0))
    .join('')}${root.files
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(fileTreeButton)
    .join('')}</div>`;
}
async function selectInitialProjectFile(tree) {
  const preferred =
      tree.find((file) => file.path === selectedFile && file.count > 0) ||
      tree.find((file) => file.count > 0) ||
      tree[0],
    button = preferred
      ? [...document.querySelectorAll('.file-item')].find((item) => item.dataset.path === preferred.path)
      : null;
  if (!button) {
    selectedFile = '';
    renderCases([]);
    return;
  }
  await selectFile(
    button.dataset.path,
    button.dataset.executable === 'true',
    button.dataset.executionKind,
    button.dataset.executionTarget,
    button.dataset.collectionState,
    button
  );
}
async function collectCases(button) {
  setButtonLoading(button, true, '收集中');
  toast('正在收集用例…');
  try {
    const result = await api(`/api/projects/${window.projectId}/collect`, {
      method: 'POST',
    });
    toast(`收集完成：${result.count} 条`);
    await loadProjectCases();
  } catch (e) {
    toast(e.message);
  } finally {
    setButtonLoading(button, false);
  }
}
async function selectFile(path, executable, executionKind, executionTarget, collectionState, el) {
  selectedFile = path;
  selectedFileExecutable = executable;
  selectedFileExecutionKind = executionKind;
  selectedFileExecutionTarget = executionTarget;
  selectedFileCollectionState = collectionState || 'source';
  selectedSource = '';
  sourceError = '';
  sourceLoading = true;
  document.querySelectorAll('.file-item').forEach((x) => x.classList.remove('active'));
  el.classList.add('active');
  filterCases();
  try {
    const data = await api(`/api/projects/${window.projectId}/source?path=${encodeURIComponent(path)}`);
    if (selectedFile === path) selectedSource = data.content;
  } catch (e) {
    if (selectedFile === path) {
      sourceError = e.message;
      toast(e.message);
    }
  } finally {
    if (selectedFile === path) {
      sourceLoading = false;
      filterCases();
    }
  }
}
function filterCases() {
  const q = (document.getElementById('case-search')?.value || '').toLowerCase(),
    mark = document.getElementById('mark-filter')?.value || '';
  renderCases(
    allCases.filter(
      (c) =>
        (!selectedFile || c.file === selectedFile) &&
        (!mark || c.markers.includes(mark)) &&
        (!q ||
          c.node_id.toLowerCase().includes(q) ||
          (c.case_id || '').toLowerCase().includes(q) ||
          (c.name || '').toLowerCase().includes(q) ||
          (c.markers || []).some((x) => x.toLowerCase().includes(q)))
    )
  );
}
function groupParameterizedCases(cases) {
  const groups = new Map();
  cases.forEach((item) => {
    const base = item.node_id.replace(/\[.*\]$/, ''),
      key = `${item.line}:${base}`;
    (
      groups.get(key) ??
      groups
        .set(key, {
          ...item,
          node_id: base,
          items: [],
        })
        .get(key)
    ).items.push(item);
  });
  return [...groups.values()];
}
function renderGutterCases(cases) {
  return groupParameterizedCases(cases)
    .map((group) => {
      const tags = [...new Set(group.items.flatMap((item) => item.markers))].filter(
          (tag) => !['allure_label', 'usefixtures', 'parametrize'].includes(tag)
        ),
        label = group.case_id || group.name.replace(/^test_/, '') || '测试',
        parameterCount =
          group.items.length > 1 ? `<span class="parameter-count">${group.items.length} 参数</span>` : '';
      return `<div class="gutter-case" title="${esc(
        group.name
      )}"><button type="button" class="gutter-run" data-target="${esc(group.node_id)}" aria-label="运行 ${esc(
        label
      )}" onclick="openRun('node',this.dataset.target)"></button><div class="gutter-meta"><strong>${esc(
        label
      )}</strong><div class="gutter-tags">${tags
        .slice(0, 2)
        .map((tag) => `<span>${esc(tag)}</span>`)
        .join('')}${
        tags.length > 2 ? `<span>+${tags.length - 2}</span>` : ''
      }${parameterCount}</div></div></div>`;
    })
    .join('');
}
function renderSourceEditor(cases) {
  const byLine = new Map();
  cases.forEach((item) => (byLine.get(item.line) ?? byLine.set(item.line, []).get(item.line)).push(item));
  const lines = selectedSource.split('\n');
  return `<div class="source-editor"><div class="source-editor-head"><span>执行</span><span>行</span><span>源代码</span></div><div class="source-lines">${lines
    .map((line, index) => {
      const number = index + 1,
        lineCases = byLine.get(number) || [];
      return `<div class="source-line ${
        lineCases.length ? 'test-source-line' : ''
      }"><div class="source-actions">${renderGutterCases(
        lineCases
      )}</div><span class="source-line-number">${number}</span><code>${
        line.length ? esc(line) : ' '
      }</code></div>`;
    })
    .join('')}</div></div>`;
}
function renderInlineSource(cases) {
  if (!selectedFile) return '';
  const body = sourceLoading
    ? '<div class="source-state">正在加载源码…</div>'
    : sourceError
    ? `<div class="source-state error">源码加载失败：${esc(sourceError)}</div>`
    : renderSourceEditor(cases);
  return `<section class="inline-source"><div class="inline-source-head"><strong>测试代码</strong><span>${esc(
    selectedFile
  )}</span></div>${body}</section>`;
}
function renderCases(items) {
  const target = document.getElementById('case-list');
  if (!selectedFile) {
    target.innerHTML = '<div class="empty">请选择左侧文件查看源码</div>';
    return;
  }
  const total = allCases.filter((c) => c.file === selectedFile).length,
    runLabel = selectedFileExecutionKind === 'feature' ? '运行 Feature' : '运行文件',
    notice =
      selectedFileCollectionState === 'not_collected'
        ? '<div class="collection-notice"><strong>未被 pytest 收集</strong><span>该文件可能被 collect_ignore、pytest 配置或命名规则排除，因此没有方法执行按钮。</span></div>'
        : '';
  target.innerHTML = `<div class="file-detail-header"><div><strong>${esc(selectedFile)}</strong>${
    total ? `<span>${items.length}${items.length !== total ? ` / ${total}` : ''} 条测试</span>` : ''
  }</div>${
    selectedFileExecutable && selectedFileExecutionKind && selectedFileExecutionTarget
      ? `<button class="button secondary" data-kind="${esc(selectedFileExecutionKind)}" data-target="${esc(
          selectedFileExecutionTarget
        )}" onclick="openRun(this.dataset.kind,this.dataset.target)">${runLabel}</button>`
      : ''
  }</div>${notice}${renderInlineSource(items)}`;
}
function openRun(kind, id) {
  document.getElementById('target-kind').value = kind;
  document.getElementById('target-id').value = id;
  document.getElementById('target-label').value = kind === 'project' ? window.projectId : id;
  document.getElementById('run-dialog').showModal();
}
function toggleProdConfirm() {
  const wrap = document.getElementById('prod-confirm-wrap');
  if (wrap) wrap.classList.toggle('hidden', document.getElementById('environment').value !== 'prod');
}
function environmentChanged() {
  toggleProdConfirm();
  const id = document.getElementById('environment').value,
    profile = (window.projectProfiles || []).find((x) => x.id === id),
    preview = document.getElementById('config-preview');
  if (!profile) {
    preview.textContent = '';
    renderRuntimeOptions([]);
    return;
  }
  const values = Object.entries(profile.summary || {})
    .map(([k, v]) => `${k}=${v}`)
    .join(' · ');
  preview.textContent = `配置来源：${profile.file}${profile.inherits ? `（继承 ${profile.inherits}）` : ''}${
    values ? ` · ${values}` : ''
  }`;
  renderRuntimeOptions(profile.runtime_options || []);
}
function runtimeOptionHtml(option) {
  const value = String(option.value ?? ''),
    common = `data-runtime-key="${esc(option.key)}" data-default="${esc(value)}"`;
  if (option.type === 'boolean')
    return `<label class="runtime-switch"><span>${esc(option.label)}<small>${esc(
      option.key
    )}</small></span><input type="checkbox" ${common} ${
      value.toLowerCase() === 'true' ? 'checked' : ''
    }></label>`;
  if (option.type === 'select')
    return `<label>${esc(option.label)}<small>${esc(option.key)}</small><select ${common}>${(
      option.choices || []
    )
      .map((x) => `<option value="${esc(x)}" ${x === value ? 'selected' : ''}>${esc(x)}</option>`)
      .join('')}</select></label>`;
  return `<label>${esc(option.label)}<small>${esc(option.key)}</small><input type="${
    option.type === 'integer'
      ? 'number'
      : option.type === 'url'
      ? 'url'
      : option.type === 'password'
      ? 'password'
      : 'text'
  }" ${common} value="${esc(value)}" placeholder="${esc(option.placeholder || '')}" ${
    option.min !== undefined ? `min="${option.min}"` : ''
  } ${option.max !== undefined ? `max="${option.max}"` : ''}></label>`;
}
function renderRuntimeOptions(options) {
  const target = document.getElementById('runtime-options');
  if (target)
    target.innerHTML = options.length
      ? options.map(runtimeOptionHtml).join('')
      : '<span class="muted">该项目没有声明可临时修改的配置</span>';
}
function resetRuntimeOptions() {
  document.querySelectorAll('[data-runtime-key]').forEach((input) => {
    if (input.type === 'checkbox') input.checked = input.dataset.default.toLowerCase() === 'true';
    else input.value = input.dataset.default;
  });
}
function collectRuntimeOverrides() {
  const values = {};
  document.querySelectorAll('[data-runtime-key]').forEach((input) => {
    const value = input.type === 'checkbox' ? String(input.checked) : input.value;
    if (value !== input.dataset.default) values[input.dataset.runtimeKey] = value;
  });
  return values;
}
async function submitRun(event) {
  event.preventDefault();
  const button = event.submitter,
    environment = document.getElementById('environment').value,
    confirmation = document.getElementById('prod-confirm');
  setButtonLoading(button, true, '创建中');
  const data = {
    project: window.projectId,
    environment,
    target: {
      type: document.getElementById('target-kind').value,
      id: document.getElementById('target-id').value,
    },
    options: {
      markers: document
        .getElementById('markers')
        .value.split(',')
        .map((x) => x.trim())
        .filter(Boolean),
      workers: Number(document.getElementById('workers').value),
      reruns: Number(document.getElementById('reruns').value),
      max_failures: 0,
    },
    runtime_overrides: collectRuntimeOverrides(),
    production_confirmation: environment === 'prod' && confirmation ? confirmation.value : '',
  };
  try {
    const run = await api('/api/runs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    location.href = `/runs/${run.id}`;
  } catch (e) {
    toast(e.message);
    setButtonLoading(button, false);
  }
}
export {
  collectCases,
  environmentChanged,
  filterCases,
  loadProjectCases,
  openRun,
  resetRuntimeOptions,
  selectFile,
  submitRun,
};
