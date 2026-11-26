// Only template event handlers are exposed; page state remains module-local.
import { setupProjectExplorerSticky, setupBackToTop, scrollRunToTop } from './common/dom.js';
import { loadProjects, loadRuns, setupRunInfiniteScroll } from './pages/dashboard.js';
import {
  loadProjectCases,
  collectCases,
  selectFile,
  filterCases,
  openRun,
  submitRun,
  resetRuntimeOptions,
  environmentChanged,
} from './pages/project.js';
import { loadRunDetail, switchRunTab, cancelRun, rerun } from './pages/run_detail.js';
import { filterAllureCases, selectAllureCase } from './reports/allure.js';
import { filterEvidence } from './reports/evidence.js';
import { showLineageNode } from './reports/lineage.js';

Object.assign(window, {
  setupProjectExplorerSticky,
  setupBackToTop,
  scrollRunToTop,
  loadProjects,
  loadRuns,
  setupRunInfiniteScroll,
  loadProjectCases,
  collectCases,
  selectFile,
  filterCases,
  openRun,
  submitRun,
  resetRuntimeOptions,
  environmentChanged,
  loadRunDetail,
  switchRunTab,
  cancelRun,
  rerun,
  filterAllureCases,
  selectAllureCase,
  filterEvidence,
  showLineageNode,
});

function initializePage() {
  if (window.projectId) {
    setupProjectExplorerSticky();
    setupBackToTop();
    loadProjectCases();
    const environment = document.getElementById('environment');
    if (environment.tagName === 'SELECT') environment.addEventListener('change', environmentChanged);
    environmentChanged();
  } else if (window.runId) {
    loadRunDetail();
  } else if (document.getElementById('project-grid')) {
    loadProjects();
    setupRunInfiniteScroll();
    loadRuns(true);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializePage, { once: true });
} else {
  initializePage();
}
