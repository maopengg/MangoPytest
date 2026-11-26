import { api } from '../common/api.js';
import {
  esc,
  setButtonLoading,
  setupBackToTop,
  setupReportSticky,
  statusText,
  toast,
} from '../common/dom.js';
import { renderAllure } from '../reports/allure.js';
let runEventSource;
function activateRunTab(name) {
  document.querySelectorAll('.run-tab').forEach((x) => x.classList.toggle('active', x.id === `tab-${name}`));
  document
    .querySelectorAll('.report-tab')
    .forEach((x) => x.classList.toggle('active', x.dataset.tab === name));
}
function switchRunTab(name) {
  activateRunTab(name);
}
function showCompletedResult() {
  setTimeout(async () => {
    try {
      await renderRun(await api(`/api/runs/${window.runId}`));
      activateRunTab('cases');
    } catch (e) {
      toast(e.message);
    }
  }, 500);
}
async function loadRunDetail() {
  setupReportSticky();
  setupBackToTop();
  try {
    const run = await api(`/api/runs/${window.runId}`);
    activateRunTab('log');
    await renderRun(run);
    const output = document.getElementById('console-output');
    output.textContent = '';
    runEventSource = new EventSource(`/api/runs/${window.runId}/events`);
    runEventSource.onmessage = (e) => {
      const item = JSON.parse(e.data);
      if (item.type === 'log') output.textContent += item.message + '\n';
      output.scrollTop = output.scrollHeight;
    };
    runEventSource.addEventListener('end', () => {
      runEventSource.close();
      document.getElementById('stream-state').textContent = '● 已结束';
      showCompletedResult();
    });
    runEventSource.onerror = () => (document.getElementById('stream-state').textContent = '● 重连中');
  } catch (e) {
    toast(e.message);
  }
}
async function renderRun(run) {
  renderAiHealing(run.id);
  const overrideText =
    Object.entries(run.runtime_overrides || {})
      .map(([k, v]) => `${k}=${v}`)
      .join(' · ') || '未修改';
  document.getElementById('run-meta').innerHTML = [
    ['项目', run.project],
    ['环境配置', run.environment],
    ['执行状态', statusText[run.status] || run.status],
    ['执行目标', run.target || '整个项目'],
    ['本次临时配置', overrideText],
  ]
    .map((x) => `<div class="meta"><span>${x[0]}</span><strong>${esc(x[1])}</strong></div>`)
    .join('');
  const cancelButton = document.getElementById('cancel-button'),
    cancelDisabled = ['passed', 'failed', 'error', 'cancelled', 'interrupted'].includes(run.status);
  if (cancelButton.dataset.loading === 'true') cancelButton._loadingDisabled = cancelDisabled;
  else cancelButton.disabled = cancelDisabled;
  const [artifacts, allure] = await Promise.all([
    api(`/api/runs/${run.id}/artifacts`),
    api(`/api/runs/${run.id}/allure`),
  ]);
  document.getElementById('artifacts').innerHTML = artifacts.length
    ? artifacts
        .map(
          (x) =>
            `<a href="/api/runs/${run.id}/artifacts/${x.path
              .split('/')
              .map(encodeURIComponent)
              .join('/')}">${esc(x.path)} · ${x.size} B</a>`
        )
        .join('')
    : '<span class="muted">产物生成中…</span>';
  renderAllure(allure, {
    projectId: run.project,
    projectKind: run.project_kind || '',
  });
}
async function cancelRun(button) {
  setButtonLoading(button, true, '停止中');
  try {
    await renderRun(
      await api(`/api/runs/${window.runId}/cancel`, {
        method: 'POST',
      })
    );
    toast('任务已停止');
  } catch (e) {
    toast(e.message);
  } finally {
    setButtonLoading(button, false);
  }
}
async function rerun(button) {
  setButtonLoading(button, true, '创建中');
  try {
    const run = await api(`/api/runs/${window.runId}/rerun`, {
      method: 'POST',
    });
    location.href = `/runs/${run.id}`;
  } catch (e) {
    toast(e.message);
    setButtonLoading(button, false);
  }
}
async function renderAiHealing(runId) {
  const panel = document.getElementById('ai-healing-panel'),
    body = document.getElementById('ai-healing-body'),
    state = document.getElementById('ai-healing-state');
  if (!panel || !body) return;
  try {
    const data = await api(`/api/runs/${runId}/ai-healing`);
    if (!data || !data.available) {
      panel.classList.add('hidden');
      return;
    }
    panel.classList.remove('hidden');
    state.textContent = `操作 ${data.operations} · 自愈 ${data.healed_operations} · AI ${data.ai_operations}`;
    const rows = [
      ['操作总数', data.operations],
      ['触发自愈', data.healed_operations],
      ['自愈成功', data.healed_successfully],
      ['自愈后仍失败', data.healed_failed],
      ['AI 调用', data.ai_operations],
      ['本地自愈', data.local_healed],
    ];
    const sources =
      Object.entries(data.by_source || {})
        .map(([k, v]) => `${k} ${v}`)
        .join(' · ') || '无';
    const elements =
      Object.entries(data.by_element || {})
        .slice(0, 10)
        .map(([k, v]) => `${k} ×${v}`)
        .join(' · ') || '无';
    const models = (data.models || []).join('、') || '未调用模型';
    const prompts = (data.prompt_versions || []).join('、') || '—';
    body.innerHTML = `<div class="meta-grid">${rows
      .map(
        ([k, v]) => `<div class="meta"><span>${esc(k)}</span><strong>${esc(String(v ?? 0))}</strong></div>`
      )
      .join('')}</div><p class="muted">定位来源：${esc(sources)}</p><p class="muted">模型：${esc(
      models
    )} · 提示词版本：${esc(prompts)}</p><p class="muted">自愈元素 Top：${esc(elements)}</p>`;
  } catch (e) {
    panel.classList.add('hidden');
  }
}
export { cancelRun, loadRunDetail, rerun, switchRunTab };
