import { esc } from '../common/dom.js';
import { renderJsonSection } from './evidence.js';
let activeLineage = null;
function lineageLevel(node) {
  return node.kind === 'factory' ? 0 : node.kind === 'operation' ? 1 : 2;
}
function lineageNodeSubtitle(node) {
  const identity = node.entity_id ? ` #${node.entity_id}` : '';
  return `${node.entity_type || node.kind}${identity}`;
}
function renderLineageSection(items) {
  const attachment = items
    ?.slice()
    .reverse()
    .find((x) => x.data?.nodes?.length);
  if (!attachment) {
    activeLineage = null;
    return '';
  }
  const graph = attachment.data;
  activeLineage = graph;
  const lanes = [[], [], []];
  graph.nodes.forEach((node) => lanes[lineageLevel(node)].push(node));
  const positions = {},
    nodeWidth = 210,
    nodeHeight = 58,
    xs = [20, 345, 670],
    gap = 30;
  lanes.forEach((nodes, level) =>
    nodes.forEach(
      (node, index) =>
        (positions[node.id] = {
          x: xs[level],
          y: 42 + index * (nodeHeight + gap),
          level,
        })
    )
  );
  const height = Math.max(180, ...lanes.map((nodes) => 70 + nodes.length * (nodeHeight + gap)));
  const edges = graph.edges
    .map((edge) => {
      const a = positions[edge.source],
        b = positions[edge.target];
      if (!a || !b) return '';
      const forward = b.x >= a.x,
        x1 = a.x + (forward ? nodeWidth : 0),
        x2 = b.x + (forward ? 0 : nodeWidth),
        y1 = a.y + nodeHeight / 2,
        y2 = b.y + nodeHeight / 2,
        mx = (x1 + x2) / 2;
      return `<g class="lineage-edge"><path d="M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}" marker-end="url(#lineage-arrow)"/><text x="${mx}" y="${
        (y1 + y2) / 2 - 5
      }">${esc(edge.relation)}</text></g>`;
    })
    .join('');
  const nodes = graph.nodes
    .map((node) => {
      const p = positions[node.id],
        title = String(node.label || node.entity_type || node.kind),
        short = title.length > 25 ? title.slice(0, 24) + '…' : title;
      return `<g class="lineage-node ${esc(node.kind)} ${esc(
        node.status
      )}" role="button" tabindex="0" aria-label="查看 ${esc(title)}" onclick="showLineageNode('${esc(
        node.id
      )}')" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showLineageNode('${esc(
        node.id
      )}')}"><rect x="${p.x}" y="${
        p.y
      }" width="${nodeWidth}" height="${nodeHeight}" rx="9"/><text class="lineage-node-title" x="${
        p.x + 13
      }" y="${p.y + 24}">${esc(short)}</text><text class="lineage-node-subtitle" x="${p.x + 13}" y="${
        p.y + 43
      }">${esc(lineageNodeSubtitle(node))}</text></g>`;
    })
    .join('');
  const s = graph.summary || {};
  return `<details class="detail-section evidence-section lineage-section filterable-evidence" data-evidence-kind="lineage" data-default-open="false"><summary><h3>数据血缘 <span>${
    graph.nodes.length
  } 节点</span></h3></summary><div class="lineage-summary"><span>Factory <strong>${
    s.factories || 0
  }</strong></span><span>操作 <strong>${s.operations || 0}</strong></span><span>实体 <strong>${
    s.entities || 0
  }</strong></span><span>关系 <strong>${
    s.relations || 0
  }</strong></span></div><div class="lineage-scroll"><svg class="lineage-graph" viewBox="0 0 900 ${height}" role="img" aria-label="测试数据血缘关系图"><defs><marker id="lineage-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z"/></marker></defs><text class="lineage-lane-title" x="20" y="20">数据工厂</text><text class="lineage-lane-title" x="345" y="20">Repository 操作</text><text class="lineage-lane-title" x="670" y="20">业务实体</text>${edges}${nodes}</svg></div><div id="lineage-node-detail" class="lineage-node-detail"><span class="muted">点击节点查看数据快照与执行状态</span></div></details>`;
}
function showLineageNode(id) {
  const node = activeLineage?.nodes?.find((x) => x.id === id),
    target = document.getElementById('lineage-node-detail');
  if (!node || !target) return;
  document
    .querySelectorAll('.lineage-node')
    .forEach((x) => x.classList.toggle('selected', x.getAttribute('onclick')?.includes(`'${id}'`)));
  const info = {
    kind: node.kind,
    label: node.label,
    entity_type: node.entity_type,
    entity_id: node.entity_id,
    source: node.source,
    status: node.status,
  };
  target.innerHTML = `<div class="lineage-detail-head"><strong>${esc(node.label)}</strong><span>${esc(
    lineageNodeSubtitle(node)
  )}</span></div>${renderJsonSection('节点信息', info, true, true)}${renderJsonSection(
    '数据快照',
    node.data,
    true,
    false
  )}`;
}
export { renderLineageSection, showLineageNode };
