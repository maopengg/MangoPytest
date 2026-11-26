import { esc, setButtonLoading, toast } from '../common/dom.js';
import { api } from '../common/api.js';
async function loadProjects(button) {
  setButtonLoading(button, true, '刷新中');
  try {
    const items = await api('/api/projects');
    document.getElementById('project-summary').textContent = `${
      items.filter((x) => x.enabled).length
    } 个可执行项目`;
    document.getElementById('project-grid').innerHTML = items
      .map(
        (p) =>
          `<a class="project-card ${p.enabled ? '' : 'disabled'}" href="/projects/${esc(
            p.id
          )}"><div class="card-top"><span class="type-pill ${esc(p.kind)}">${esc(
            p.kind
          ).toUpperCase()}</span>${
            p.latest ? `<span class="status ${esc(p.latest.status)}">${esc(p.latest.status)}</span>` : ''
          }</div><h3>${esc(p.id)}</h3><p>${esc(p.name)}${
            p.reason ? ' · ' + esc(p.reason) : ''
          }</p><div class="card-bottom"><span class="count">${
            p.collected ? p.case_count : '—'
          } 条用例</span><span>查看 →</span></div></a>`
      )
      .join('');
  } catch (e) {
    toast(e.message);
  } finally {
    setButtonLoading(button, false);
  }
}
const RUN_PAGE_SIZE = 20;
let runsOffset = 0,
  runsLoading = false,
  runsComplete = false;
function renderRunRows(items) {
  return items
    .map(
      (r) =>
        `<a class="run-row" href="/runs/${r.id}"><strong>${esc(r.project)}</strong><span>${esc(
          r.target_kind
        )} · ${esc(r.environment)}</span><span class="status ${esc(r.status)}">${esc(r.status)}</span><span>${
          r.passed
        }/${r.total} 通过</span><span>详情 →</span></a>`
    )
    .join('');
}
function renderRunListStatus(target) {
  target.querySelector('.run-list-status')?.remove();
  if (runsOffset === 0) return;
  target.insertAdjacentHTML(
    'beforeend',
    `<div class="run-list-status">${
      runsLoading ? '正在加载…' : runsComplete ? `已加载全部 ${runsOffset} 条本地记录` : '向下滚动加载更多'
    }</div>`
  );
}
async function loadRuns(reset = true, button) {
  const target = document.getElementById('run-list');
  if (!target || runsLoading || (!reset && runsComplete)) return;
  setButtonLoading(button, true, '刷新中');
  if (reset) {
    runsOffset = 0;
    runsComplete = false;
    target.innerHTML = '<div class="run-list-status">正在读取本地执行记录…</div>';
    target.scrollTop = 0;
  }
  runsLoading = true;
  renderRunListStatus(target);
  try {
    const items = await api(`/api/runs?limit=${RUN_PAGE_SIZE}&offset=${runsOffset}`);
    if (reset) target.innerHTML = '';
    if (!items.length && runsOffset === 0) {
      target.innerHTML = '<div class="empty">暂无执行记录</div>';
      runsComplete = true;
      return;
    }
    target.querySelector('.run-list-status')?.remove();
    target.insertAdjacentHTML('beforeend', renderRunRows(items));
    runsOffset += items.length;
    runsComplete = items.length < RUN_PAGE_SIZE;
  } catch (e) {
    toast(e.message);
  } finally {
    runsLoading = false;
    renderRunListStatus(target);
    setButtonLoading(button, false);
  }
}
function setupRunInfiniteScroll() {
  const target = document.getElementById('run-list');
  if (!target) return;
  target.addEventListener(
    'scroll',
    () => {
      if (target.scrollHeight - target.scrollTop - target.clientHeight < 100) loadRuns(false);
    },
    {
      passive: true,
    }
  );
}
export { loadProjects, loadRuns, setupRunInfiniteScroll };
