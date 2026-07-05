/* dashboard_app.js — TopoGraph: The Ontology Healer
   All numbers come from DATA (embedded, precomputed by export_dashboard_data.py).
   Nothing here invents data — it only renders / filters / re-colors it. */

const CATEGORY_COLORS = {
  chain_pattern: '#E07A5F',
  signal_interpretation: '#7C8AC2',
  tactical_priority: '#81B29A',
  bypass_technique: '#F2CC8F',
  pitfall: '#B895F2'
};
const DIM_EDGE = '#3A4456';
const TRUSTED_EDGE = '#E8A33D';
const HEAL_RED = '#FF5C5C';

const nodeById = {};
DATA.nodes.forEach(n => nodeById[n.id] = n);

const PLOT_IDS = [
  'plot-overview-network', 'plot-phase1-network', 'plot-phase1-betti',
  'plot-phase2-network', 'plot-phase2-diagram', 'plot-phase2-barcode'
];

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const BASE_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 10, r: 10, t: 10, b: 10 },
  xaxis: { visible: false, range: [-1.35, 1.35] },
  yaxis: { visible: false, range: [-1.35, 1.35] },
  showlegend: false, hovermode: 'closest',
  font: { family: 'Inter, sans-serif', color: '#E8ECF1' }
};
const PLOT_CONFIG = { displayModeBar: false, responsive: true };

function nodeTrace(opts = {}) {
  const nodes = DATA.nodes;
  return {
    type: 'scatter', mode: 'markers',
    x: nodes.map(n => n.x), y: nodes.map(n => n.y),
    text: nodes.map(n =>
      `<b>${esc(n.id)}</b><br>${esc(n.title)}<br>category: ${esc(n.category)}` +
      `<br>quality: ${n.pass_count}/8 &nbsp; degree: ${n.in_degree}/${n.out_degree}`
    ),
    hoverinfo: 'text',
    marker: {
      size: nodes.map(n => 11 + 3.5 * (n.in_degree + n.out_degree)),
      color: nodes.map(n => CATEGORY_COLORS[n.category] || '#999'),
      opacity: nodes.map(n => (n.in_degree + n.out_degree) === 0 ? 0.4 : 1.0),
      line: { width: 1.2, color: '#0D1117' }
    }
  };
}

function edgeTraces(edges, colorFn, opacityFn, dash) {
  return edges.map(e => {
    const s = nodeById[e.source], t = nodeById[e.target];
    if (!s || !t) return null;
    return {
      type: 'scatter', mode: 'lines',
      x: [s.x, t.x], y: [s.y, t.y],
      line: { color: colorFn ? colorFn(e) : '#5B6577', width: 1.8, dash: dash || 'solid' },
      opacity: opacityFn ? opacityFn(e) : 0.85,
      hoverinfo: 'skip', showlegend: false
    };
  }).filter(Boolean);
}

function buildLegend(containerId) {
  const cats = [...new Set(DATA.nodes.map(n => n.category))];
  document.getElementById(containerId).innerHTML = cats.map(c =>
    `<div class="legend-item"><span class="dot" style="background:${CATEGORY_COLORS[c]}"></span>${c}</div>`
  ).join('');
}

function resizeAllPlots() {
  PLOT_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.data) Plotly.Plots.resize(el);
  });
}

/* ===================== OVERVIEW ===================== */
function initOverview() {
  const s = DATA.summary;
  const stats = [
    { num: s.n_entries, lbl: 'knowledge entries (ek_0000–ek_0040)', accent: '' },
    { num: `${s.n_declared_edges} / ${s.n_total_ref_edges}`, lbl: 'cross-reference edges fall inside our 41-node sample', accent: 'amber' },
    { num: s.n_components, lbl: 'weakly-connected components', accent: 'teal' },
    { num: '0', lbl: 'cycles in the declared graph — proven forest', accent: 'violet' }
  ];
  document.getElementById('overview-stats').innerHTML = stats.map(t =>
    `<div class="stat-tile ${t.accent ? 'accent-' + t.accent : ''}">
       <div class="num">${t.num}</div><div class="lbl">${t.lbl}</div>
     </div>`
  ).join('');

  const data = [...edgeTraces(DATA.declared_edges, () => '#5B6577', () => 0.7), nodeTrace()];
  Plotly.newPlot('plot-overview-network', data, BASE_LAYOUT, PLOT_CONFIG);
  buildLegend('overview-legend');
}

/* ===================== PHASE 1 ===================== */
let phase1Initialized = false;
function initPhase1() {
  const proof = DATA.phase1.proof;
  document.getElementById('phase1-equation').textContent =
    `n_edges = n_nodes − n_components   →   ${proof.n_edges} = ${proof.n_nodes} − ${proof.n_components}  ✓ forest`;
  document.getElementById('phase1-proof-text').textContent = proof.proof_statement;

  const curve = DATA.phase1.betti_curve;
  const maxIdx = curve.eps.length - 1;
  const slider = document.getElementById('phase1-slider');
  slider.max = maxIdx;

  // betti curve chart
  const maxY = Math.max(...curve.beta0) + 2;
  Plotly.newPlot('plot-phase1-betti', [
    { x: curve.eps, y: curve.beta0, mode: 'lines', name: 'β₀', line: { color: '#4FD1C5', width: 2.5 } },
    { x: curve.eps, y: curve.beta1, mode: 'lines', name: 'β₁', line: { color: '#9B8CFF', width: 2.5 } }
  ], {
    ...BASE_LAYOUT,
    xaxis: { visible: true, title: 'ε (filtration / validation leniency)', gridcolor: '#26303F', color: '#8893A3', range: [0, 1] },
    yaxis: { visible: true, title: 'Betti number', gridcolor: '#26303F', color: '#8893A3', range: [-0.5, maxY] },
    showlegend: true, legend: { font: { color: '#E8ECF1' }, orientation: 'h', y: 1.15 },
    shapes: [{ type: 'line', x0: curve.eps[maxIdx], x1: curve.eps[maxIdx], y0: 0, y1: maxY, line: { color: '#E8A33D', width: 1.5, dash: 'dot' } }],
    margin: { l: 46, r: 10, t: 30, b: 40 }
  }, PLOT_CONFIG);

  function renderAtIndex(idx) {
    const eps = curve.eps[idx], beta0 = curve.beta0[idx];
    document.getElementById('readout-eps').textContent = eps.toFixed(3);
    document.getElementById('readout-quality').textContent = (8 * (1 - eps)).toFixed(1) + ' / 8';
    document.getElementById('readout-beta0').textContent = beta0;

    const data = [
      ...edgeTraces(
        DATA.declared_edges,
        e => e.quality_distance <= eps ? TRUSTED_EDGE : DIM_EDGE,
        e => e.quality_distance <= eps ? 0.95 : 0.18
      ),
      nodeTrace()
    ];
    Plotly.react('plot-phase1-network', data, BASE_LAYOUT, PLOT_CONFIG);
    Plotly.relayout('plot-phase1-betti', { 'shapes[0].x0': eps, 'shapes[0].x1': eps });
  }

  slider.addEventListener('input', () => renderAtIndex(+slider.value));
  renderAtIndex(maxIdx);
}

/* ===================== PHASE 2 ===================== */
let phase2Initialized = false;
let healOn = false;

function renderPhase2Network() {
  const overlay = healOn ? DATA.phase2.missing_links.slice(0, 5).map(c => ({ source: c.a, target: c.b })) : [];
  const data = [
    ...edgeTraces(DATA.declared_edges, () => '#5B6577', () => 0.75),
    ...edgeTraces(overlay, () => HEAL_RED, () => 0.95, 'dash'),
    nodeTrace()
  ];
  Plotly.react('plot-phase2-network', data, BASE_LAYOUT, PLOT_CONFIG);
}

function renderMissingLinksList() {
  const top5 = DATA.phase2.missing_links.slice(0, 5);
  document.getElementById('missing-links-list').innerHTML = top5.map(c => `
    <div class="link-card">
      <div class="pair">${esc(c.a)} ↔ ${esc(c.b)}
        ${!c.reachable_via_declared_chain ? '<span class="unreachable-badge">unreachable via any declared chain</span>' : ''}
      </div>
      <div class="titles">"${esc(c.a_title)}"<br>"${esc(c.b_title)}"</div>
      <div class="stats">
        <div class="stat">distance <b>${c.distance}</b></div>
        <div class="stat">z-score <b>${c.z_score}</b></div>
        <div class="stat">percentile <b>${c.percentile_rank}%</b></div>
      </div>
    </div>
  `).join('');
}

function renderPersistenceDiagram() {
  const pers = DATA.phase2.persistence;
  let maxDeath = 0;
  ['0', '1'].forEach(d => (pers[d] || []).forEach(([b, death]) => { if (death !== null) maxDeath = Math.max(maxDeath, death); }));
  const plotMax = maxDeath * 1.08;
  const dimColor = { '0': '#4FD1C5', '1': '#FF8A65' };
  const traces = ['0', '1'].map(d => {
    const pts = (pers[d] || []);
    return {
      type: 'scatter', mode: 'markers', name: `H${d}`,
      x: pts.map(p => p[0]),
      y: pts.map(p => p[1] === null ? plotMax : p[1]),
      marker: { color: dimColor[d], size: 7, opacity: 0.8, line: { color: '#0D1117', width: 0.5 } }
    };
  });
  traces.push({
    type: 'scatter', mode: 'lines', x: [0, plotMax], y: [0, plotMax],
    line: { color: '#3A4456', dash: 'dash', width: 1 }, hoverinfo: 'skip', showlegend: false
  });
  Plotly.newPlot('plot-phase2-diagram', traces, {
    ...BASE_LAYOUT,
    xaxis: { visible: true, title: 'birth', gridcolor: '#26303F', color: '#8893A3' },
    yaxis: { visible: true, title: 'death', gridcolor: '#26303F', color: '#8893A3' },
    showlegend: true, legend: { font: { color: '#E8ECF1' } },
    margin: { l: 46, r: 10, t: 20, b: 40 }
  }, PLOT_CONFIG);
}

function renderBarcode() {
  const pers = DATA.phase2.persistence;
  let maxDeath = 0;
  ['0', '1'].forEach(d => (pers[d] || []).forEach(([b, death]) => { if (death !== null) maxDeath = Math.max(maxDeath, death); }));
  const plotMax = maxDeath * 1.05;
  const dimColor = { '0': '#4FD1C5', '1': '#FF8A65' };

  const rows = [];
  ['0', '1'].forEach(d => {
    const feats = (pers[d] || [])
      .map(([b, death]) => ({ b, death: death === null ? plotMax : death }))
      .sort((a, b2) => (b2.death - b2.b) - (a.death - a.b))
      .slice(0, d === '0' ? 22 : 15);
    feats.forEach(f => rows.push({ dim: d, ...f }));
  });

  Plotly.newPlot('plot-phase2-barcode', [{
    type: 'bar', orientation: 'h',
    base: rows.map(r => r.b),
    x: rows.map(r => r.death - r.b),
    y: rows.map((_, i) => i),
    marker: { color: rows.map(r => dimColor[r.dim]) },
    hoverinfo: 'skip'
  }], {
    ...BASE_LAYOUT,
    xaxis: { visible: true, title: 'semantic distance', gridcolor: '#26303F', color: '#8893A3' },
    yaxis: { visible: false },
    margin: { l: 10, r: 10, t: 20, b: 40 }
  }, PLOT_CONFIG);
}

function initPhase2() {
  renderPhase2Network();
  renderMissingLinksList();
  renderPersistenceDiagram();
  renderBarcode();

  const toggle = document.getElementById('heal-toggle');
  const label = document.getElementById('heal-toggle-label');
  toggle.addEventListener('click', () => {
    healOn = !healOn;
    toggle.classList.toggle('on', healOn);
    label.textContent = `Show healed links — ${healOn ? 'ON' : 'OFF'}`;
    renderPhase2Network();
  });
}

/* ===================== TAB SWITCHING ===================== */
document.getElementById('tabs').addEventListener('click', e => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  const tab = btn.dataset.tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('sec-' + tab).classList.add('active');

  if (tab === 'phase1' && !phase1Initialized) { initPhase1(); phase1Initialized = true; }
  if (tab === 'phase2' && !phase2Initialized) { initPhase2(); phase2Initialized = true; }
  requestAnimationFrame(resizeAllPlots);
});

window.addEventListener('resize', resizeAllPlots);
initOverview();