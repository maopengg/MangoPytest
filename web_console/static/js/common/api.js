let pendingApiRequests = 0,
  apiLoadingTimer = 0;
function beginApiLoading() {
  pendingApiRequests += 1;
  document.body.setAttribute('aria-busy', 'true');
  if (pendingApiRequests === 1)
    apiLoadingTimer = setTimeout(() => {
      const indicator = document.getElementById('global-api-loading');
      if (indicator) indicator.hidden = false;
    }, 120);
}
function endApiLoading() {
  pendingApiRequests = Math.max(0, pendingApiRequests - 1);
  if (pendingApiRequests) return;
  clearTimeout(apiLoadingTimer);
  document.body.removeAttribute('aria-busy');
  const indicator = document.getElementById('global-api-loading');
  if (indicator) indicator.hidden = true;
}
async function api(url, options = {}) {
  beginApiLoading();
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });
    if (!response.ok) {
      let detail = response.statusText;
      try {
        detail = (await response.json()).detail || detail;
      } catch {}
      throw new Error(detail);
    }
    return response.json();
  } finally {
    endApiLoading();
  }
}
export { api };
