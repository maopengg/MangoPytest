const esc = (v) =>
  String(v ?? '').replace(
    /[&<>'"]/g,
    (c) =>
      ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;',
      }[c])
  );
function toast(message) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2600);
}
function setButtonLoading(button, loading, label = '加载中') {
  if (!button) return;
  if (loading) {
    if (button.dataset.loading === 'true') return;
    button.dataset.loading = 'true';
    button._loadingContent = button.innerHTML;
    button._loadingDisabled = button.disabled;
    button._loadingMinWidth = button.style.minWidth;
    button.style.minWidth = `${button.offsetWidth}px`;
    button.disabled = true;
    button.classList.add('is-loading');
    button.setAttribute('aria-busy', 'true');
    button.innerHTML = `<span class="loading-spinner" aria-hidden="true"></span><span>${esc(label)}</span>`;
    return;
  }
  if (button.dataset.loading !== 'true') return;
  button.innerHTML = button._loadingContent;
  button.disabled = button._loadingDisabled;
  button.style.minWidth = button._loadingMinWidth;
  button.classList.remove('is-loading');
  button.removeAttribute('aria-busy');
  delete button.dataset.loading;
}
const statusText = {
  passed: '通过',
  failed: '失败',
  broken: '异常',
  skipped: '跳过',
  unknown: '未知',
};
function setupReportSticky() {
  const shell = document.querySelector('.report-shell'),
    anchor = shell?.closest('.report-anchor');
  if (!shell || !anchor) return;
  let frame = 0;
  const update = () => {
    frame = 0;
    const desktop = window.matchMedia('(min-width: 901px)').matches,
      rect = anchor.getBoundingClientRect(),
      reached = rect.top <= 0.5 && rect.bottom > 0;
    shell.style.setProperty('--report-left', `${rect.left}px`);
    shell.style.setProperty('--report-width', `${rect.width}px`);
    shell.classList.toggle('is-pinned', desktop && reached);
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };
  window.addEventListener('scroll', schedule, {
    passive: true,
  });
  window.addEventListener('resize', schedule, {
    passive: true,
  });
  update();
}
function setupProjectExplorerSticky() {
  const explorer = document.querySelector('.explorer'),
    anchor = explorer?.closest('.explorer-anchor');
  if (!explorer || !anchor) return;
  let frame = 0;
  const update = () => {
    frame = 0;
    const desktop = window.matchMedia('(min-width: 901px)').matches,
      rect = anchor.getBoundingClientRect(),
      reached = rect.top <= 0.5 && rect.bottom > 0;
    explorer.style.setProperty('--explorer-left', `${rect.left}px`);
    explorer.style.setProperty('--explorer-width', `${rect.width}px`);
    explorer.classList.toggle('is-pinned', desktop && reached);
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };
  window.addEventListener('scroll', schedule, {
    passive: true,
  });
  window.addEventListener('resize', schedule, {
    passive: true,
  });
  update();
}
function setupBackToTop() {
  const button = document.getElementById('back-to-top');
  if (!button) return;
  let frame = 0;
  const update = () => {
    frame = 0;
    button.classList.toggle('visible', window.scrollY > 240);
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };
  window.addEventListener('scroll', schedule, {
    passive: true,
  });
  update();
}
function scrollRunToTop() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    behavior = reduced ? 'auto' : 'smooth';
  document
    .querySelectorAll(
      '.allure-case-list,.allure-case-detail,#tab-log,#tab-artifacts,.file-tree,.case-list,.source-editor'
    )
    .forEach((element) =>
      element.scrollTo({
        top: 0,
        left: 0,
        behavior,
      })
    );
  window.scrollTo({
    top: 0,
    behavior,
  });
}
function formatDuration(ms) {
  if (!ms) return '0 ms';
  if (ms < 1000) return `${ms} ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)} s`;
  return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(1)}s`;
}
function formatTime(ms) {
  return ms
    ? new Date(ms).toLocaleString('zh-CN', {
        hour12: false,
      })
    : '—';
}
export {
  esc,
  formatDuration,
  formatTime,
  scrollRunToTop,
  setButtonLoading,
  setupBackToTop,
  setupProjectExplorerSticky,
  setupReportSticky,
  statusText,
  toast,
};
